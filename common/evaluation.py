import models
import os
import config
import shutil
import sqlite3
import json
from config import *
import sqlparse
import Levenshtein
import sqlparse.keywords
from common.for_sqlite import recover_schema
from common.segment import Segment
# import re

from flask_restful import abort


def evaluation(submit: models.Submit):
    syntax_error_msg = ""

    type_ = None

    schema = submit.Question.Schema
    question = submit.Question
    answers = models.Answer.query.filter_by(idQuestion=question.id)
    student = submit.Student

    recover_schema(schema)

    path = os.path.join(config.save_db_path, student.id)
    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.join(path, schema.name)
    shutil.copyfile(schema.path, path)

    correct_sql, count_spelling_err, answer, correct = correct_spelling(submit.answer, list(answers), schema, )
    submit.correct = correct_sql
    submit.spelling = count_spelling_err
    submit.idAnswer = answer.id
    submit.Answer = answer

    conn = sqlite3.connect(path)
    cur = conn.cursor()
    try:
        cur.execute(correct_sql)
        values = cur.fetchall()
        result = {'data': values, 'len': len(values)}
        submit.result = json.dumps(result)
        result = json.loads(submit.result)
        if question.result is None:
            abort(500)
        else:
            origin = json.loads(question.result)
            if origin == result:
                submit.score = question.score - count_spelling_err
                submit.info = ' '.join(map(str, correct)) + '\n' + syntax_error_msg
                type_ = type_submit.all_right if count_spelling_err == 0 else type_submit.error_spelling
            else:
                type_ = type_submit.error_result
    except Exception as e:
        syntax_error_msg = str(e)
        submit.result = str(e)
        type_ = type_submit.error_syntax
    finally:
        cur.close()
        conn.close()

    submit.segmentJson = json.dumps({'compare': []})
    if type_ != type_submit.error_spelling and type_ != type_submit.all_right:
        submit.info = ' '.join(map(str, correct)) + '\n' + syntax_error_msg
        if type_ == type_submit.error_result:
            submit.score = question.score - count_spelling_err
            stu_segments = Segment(submit.correct)
            segments = models.Segmentation.query.filter_by(idAnswer=submit.Answer.id).order_by(models.Segmentation.rank)
            segments = [s for s in segments]
            submit.segmentJson = {'compare': []}
            idx_student_segment = 0
            idx_segment = 0
            while idx_segment < len(segments):
                compare = {'right_segment': segments[idx_segment].data}
                if idx_student_segment < len(stu_segments.segment_str) and Segment.filter_segment_punctuation(
                        segments[idx_segment].data) == Segment.filter_segment_punctuation(
                        stu_segments.segment_str[idx_student_segment]):
                    compare['student_segment'] = stu_segments.segment_str[idx_student_segment]
                    compare['deduction'] = 0
                    idx_student_segment += 1
                else:
                    tmp_idx = idx_student_segment
                    max_score = 0
                    max_idx = tmp_idx
                    while tmp_idx < len(stu_segments.segment_str):
                        score = Levenshtein.ratio(Segment.filter_segment_punctuation(segments[idx_segment].data),
                                                  Segment.filter_segment_punctuation(stu_segments.segment_str[tmp_idx]))
                        if score > max_score:
                            max_idx = tmp_idx
                            max_score = score
                        tmp_idx += 1
                    if max_score < 0.6:
                        compare['student_segment'] = ''
                        compare['deduction'] = segments[idx_segment].score
                        submit.score -= segments[idx_segment].score
                    else:
                        compare['student_segment'] = stu_segments.segment_str[max_idx]
                        while idx_student_segment < max_idx:
                            submit.segmentJson['compare'].append({
                                'student_segment': stu_segments.segment_str[idx_student_segment],
                                'right_segment': '',
                                'deduction': 2
                            })
                            submit.score -= 2
                            idx_student_segment += 1
                        idx_student_segment = max_idx + 1
                        if max_score == 1:
                            compare['deduction'] = 0
                        else:
                            compare['deduction'] = segments[idx_segment].score
                            submit.score -= segments[idx_segment].score

                idx_segment += 1
                submit.segmentJson['compare'].append(compare)
            while idx_student_segment < len(stu_segments.segment_str):
                submit.segmentJson['compare'].append({
                    'student_segment': stu_segments.segment_str[idx_student_segment],
                    'right_segment': '',
                    'deduction': 2
                })
                submit.score -= 2
                idx_student_segment += 1

        elif type_ == type_submit.error_syntax:
            submit.score = 0
            pass
    submit.score = 0 if submit.score < 0 else submit.score
    submit.segmentJson = json.dumps(submit.segmentJson)
    submit.type = type_.value
    os.remove(path)


def correct_spelling(stem, answers, schema):
    keywords_schema = schema.keywords.split(' ')
    keywords_schema.append('*')
    format_sql = sqlparse.format(stem, keyword_case='upper')
    correct = [0] * len(format_sql)
    format_sql += '\0'
    # segment_sql = re.split('[. \t\n]', format_sql)
    correct_sql = ''
    start_word_idx = 0
    count_spelling_err = 0
    keywords = [keywords_schema, list(sqlparse.keywords.KEYWORDS.keys()),
                list(sqlparse.keywords.KEYWORDS_COMMON.keys())]
    for i in range(0, len(format_sql)):
        if format_sql[i] in (' ', '.', '\0', '=', '<', '>', '!', ',', ')', '(') or format_sql[i].isdigit():
            word = format_sql[start_word_idx:i]

            if word.strip() != '' and word not in keywords[0] and word.upper() not in keywords[
                1] and word.upper() not in keywords[2]:
                count_spelling_err += 1
                max_word = ''
                max_value = 0
                done = False
                for idx in range(0, len(keywords)):
                    if idx > 1:
                        word = word.upper()
                    for j in range(0, len(keywords[idx])):
                        ratio = Levenshtein.ratio(word, keywords[idx][j])
                        if ratio > replace_threshold:
                            done = True
                            max_word = keywords[idx][j]
                            max_value = ratio
                            break
                        elif ratio > max_value:
                            max_word = keywords[idx][j]
                            max_value = ratio
                    if done:
                        break
                correct_sql += max_word
                correct = list(
                    map(lambda idx, x: round(max_value, 3) if start_word_idx <= idx < i else x, range(0, len(correct)),
                        correct))
            else:
                correct_sql += word

            if format_sql[i] != '\0':
                correct_sql += format_sql[i]
            start_word_idx = i + 1
        else:
            correct[i] = 1
    max_answer = answers[0]
    max_value = Levenshtein.ratio(answers[0].sql, correct_sql)
    for i in range(1, len(answers)):
        ratio = Levenshtein.ratio(answers[i].sql, correct_sql)
        if ratio > max_value:
            max_answer = answers[i]
            max_value = ratio

    return correct_sql, count_spelling_err, max_answer, correct

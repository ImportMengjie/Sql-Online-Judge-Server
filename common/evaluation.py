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
# import re

from flask_restful import abort


def evaluation(submit: models.Submit):
    syntax_error_msg = ""

    type_ = None

    schema = submit.Question.Schema
    question = submit.Question
    answers = models.Answer.query.filter_by(idQuestion=question.id)
    student = submit.Student

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
    if type_ != type_submit.error_spelling and type_ != type_submit.all_right:
        submit.score = 0
        submit.info = ''.join(map(str, correct)) + '\n' + syntax_error_msg
    else:
        pass
    submit.type = type_.value
    os.remove(path)


def correct_spelling(stem, answers, schema):
    keywords_schema = schema.keywords.split(' ')
    keywords_schema.append('*')
    formated_sql = sqlparse.format(stem, keyword_case='upper')
    correct = [0] * len(formated_sql)
    # segment_sql = re.split('[. \t\n]', formated_sql)
    correct_sql = ''
    start_word_idx = 0
    count_spelling_err = 0
    keywords = [keywords_schema, list(sqlparse.keywords.KEYWORDS.keys()),
                list(sqlparse.keywords.KEYWORDS_COMMON.keys())]
    for i in range(0, len(formated_sql)):
        if formated_sql[i] == ' ' or formated_sql[i] == '.' or i == len(formated_sql)-1:
            word = formated_sql[start_word_idx:i if i<len(formated_sql)-1 else i+1]
            if word not in keywords[0] and word.upper() not in keywords[1] and word.upper() not in keywords[2]:
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
                    map(lambda idx, x: max_value if start_word_idx<=idx<i else x, range(0, len(correct)), correct))
            else:
                correct_sql += word

            if len(formated_sql)-1 > i:
                correct_sql += formated_sql[i]
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

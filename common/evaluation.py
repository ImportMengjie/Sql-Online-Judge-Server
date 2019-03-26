import models
import os
import config
import shutil
import sqlite3
import json
from config import *

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

    correct = [0] * len(submit.answer)
    student_answer, count_spelling_err, answer = correct_spelling(submit.answer, answers, correct)
    submit.spelling = count_spelling_err
    submit.idAnswer = answer.id
    submit.Answer = answer

    conn = sqlite3.connect(path)
    cur = conn.cursor()
    try:
        cur.execute(student_answer)
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
                submit.info = ''.join(map(str, correct)) + '\n' + syntax_error_msg
                type_ = type_submit.all_right if count_spelling_err == 0 else type_submit.error_spelling
            else:
                type_ = type_submit.error_result
    except Exception as e:
        syntax_error_msg = str(e)
        submit.result = str(e)
        type_ = type_submit.error_syntax
    finally:
        conn.close()
    if type_ != type_submit.error_spelling and type_ != type_submit.all_right:
        submit.score = 0
        submit.info = ''.join(map(str, correct)) + '\n' + syntax_error_msg
    else:
        pass
    submit.type = type_.value
    os.remove(path)


def correct_spelling(stem, answers, correct):
    return stem, 0, answers[0]

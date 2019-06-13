from flask_restful import Resource, fields, marshal_with, marshal, reqparse
import models
from exts import db
from common.comm import auth_admin, auth_all, auth_student
from config import *
from flask import request
import common.evaluation
import json
from config import type_submit

submit_field = {
    'id': fields.Integer,
    'idStudent': fields.String,
    'idQuestion': fields.Integer,
    'score': fields.Integer,
    'answer': fields.String,
    'time': fields.DateTime,
    'info': fields.String,
    'type': fields.Integer
}


class Submits(Resource):

    @auth_all()
    @marshal_with(submit_field)
    def get(self, admin, student, submit_id, idStudent):
        if student is not None and student.id != idStudent:
            return get_common_error_dic("you not allow to access this resource"), HTTP_Forbidden
        ret = models.Answer.query.filter_by(id=submit_id).first()
        if ret is not None:
            return ret, HTTP_OK
        else:
            return {}, HTTP_NotFound

    @auth_admin(False)
    def delete(self, submit_id, idStudent):
        ret = models.Answer.query.filter_by(id=submit_id).first()
        if ret is not None:
            db.session.delete(ret)
            db.session.commit()
            return {}, HTTP_OK
        else:
            return {}, HTTP_NotFound


class SubmitList(Resource):

    @auth_all(inject=True)
    def get(self, admin, student, idQuestion=None, idStudent=None):
        if idQuestion is None and idStudent is None and student is not None:
            submits = models.Submit.query.filter_by(idStudent=student.id)
        elif idQuestion is None and idStudent is None and admin is not None:
            submits = models.Submit.query.filter_by()
        elif idQuestion is None and student is not None:
            submits = models.Submit.query.filter_by(idStudent=student.id)
        elif idQuestion is not None and idStudent is None:
            submits = models.Submit.query.filter_by(idQuestion=idQuestion)
        else:
            submits = models.Submit.query.filter_by(idQuestion=idQuestion, idStudent=idStudent)
        data = []
        for submit in submits:
            ret = marshal(submit, submit_field)
            ret['relative_score'] = int((submit.score / submit.Question.score) * 10)
            data.append(ret)
        ret = {'data': data}
        if student is not None:
            for_score_chart = [0] * 11
            for_type_chart = [{'value': 0, 'name': it.name} for it in type_submit]
            for submit in data:
                for_score_chart[submit['relative_score']] += 1
                for_type_chart[submit['type']]['value'] += 1
            ret['chart'] = {'score': for_score_chart, 'type': for_type_chart}
            ret['type_name'] = []
            for t in type_submit:
                ret['type_name'].append(t.name)
        return ret, HTTP_OK

    @auth_student()
    def post(self, idQuestion, student, idStudent=None):
        if idStudent is not None and idStudent != student.id:
            return get_common_error_dic('student id not match your account!'), HTTP_Forbidden
        submit = models.Submit()
        submit.Student = student
        submit.idQuestion = idQuestion
        question = models.Question.query.get(idQuestion)
        submit.answer = request.json.get('answer')
        submit.Question = question
        if question is None:
            return get_common_error_dic('question id is wrong'), HTTP_Bad_Request
        if submit.answer is None:
            return get_shortage_error_dic('answer'), HTTP_Bad_Request
        submit.answer = submit.answer.strip()
        common.evaluation.evaluation(submit)
        db.session.add(submit)
        db.session.commit()
        if submit.type != type_submit.error_syntax.value:
            right_result = json.loads(submit.Question.result)['data']
            result = json.loads(submit.result)['data']
            compare_result = []
            idx_right_result = 0
            idx_result = 0
            while idx_result < len(result) and idx_right_result < len(right_result):
                compare_result.append(
                    {'your_result': str(result[idx_result]), 'right_result': str(right_result[idx_right_result])})
                idx_result += 1
                idx_right_result += 1
            while idx_result < len(result):
                compare_result.append({'your_result': str(result[idx_result]), 'right_result': ''})
                idx_result += 1
            while idx_right_result < len(right_result):
                compare_result.append({'your_result': '', 'right_result': str(right_result[idx_right_result])})
                idx_right_result += 1
        else:
            compare_result = []
        return {
                   'id': submit.id,
                   'type': submit.type,
                   'type_info': str(type_submit(submit.type)),
                   'info': submit.info,
                   'time': submit.time.isoformat(),
                   'score': submit.score,
                   'right_answer': submit.Answer.sql,
                   'your_answer': submit.answer,
                   'correct': submit.correct,
                   'spelling_count': submit.spelling,
                   'result': submit.result,
                   'right_result': submit.Question.result,
                   'segment_json': json.loads(submit.segmentJson),
                   'compare_result': compare_result
               }, HTTP_Created

from flask_restful import Resource, fields, marshal_with, marshal
import models
from exts import db
from common.comm import auth_admin, auth_all
from config import *
from flask import request
import moz_sql_parser
import json
import sqlite3

answer_field = {
    'id': fields.Integer,
    'idQuestion': fields.Integer,
    'data': fields.String,
    'json': fields.String,
}


class Answers(Resource):

    @auth_all(False)
    @marshal_with(answer_field)
    def get(self, idQuestion, answer_id):
        ret = models.Answer.query.filter_by(id=answer_id).first()
        if ret is not None:
            return ret, HTTP_OK
        else:
            return {}, HTTP_NotFound

    @auth_admin(False)
    def delete(self, idQuestion, answer_id):
        ret = models.Answer.query.filter_by(id=answer_id).first()
        if ret is not None:
            db.session.delete(ret)
            db.session.commit()
            return {}, HTTP_OK
        else:
            return {}, HTTP_NotFound

    # TODO: when update answer , we need update question's result sometimes
    @auth_admin(False)
    def patch(self, answer_id):
        ret = models.Answer.query.filter_by(id=answer_id).first()
        if ret is not None:
            pass
        else:
            return {}, HTTP_NotFound


class AnswerList(Resource):

    @auth_all(inject=False)
    def get(self, idQuestion):
        answers = models.Answer.query.filter_by(idQuestion=idQuestion)
        data = [marshal(answer, answer_field) for answer in answers]
        return {'data': data}, HTTP_OK

    # NOTE: Answer sql
    @auth_admin(inject=False)
    def post(self, idQuestion):
        answer = models.Answer()
        answer.idQuestion = idQuestion
        question = models.Question.query.get(answer.idQuestion)
        answer.sql = request.json.get('data')
        if answer.idQuestion is None or answer.sql is None:
            return get_shortage_error_dic("idQuestion data"), HTTP_Bad_Request
        if question is None:
            return get_common_error_dic("question id is wrong"), HTTP_Bad_Request
        try:
            parsed = moz_sql_parser.parse(answer.sql)
            answer.json = json.dumps(parsed)
        except Exception as e:
            return get_except_error(e)
        # TODO: gen segmentation, gen result
        schema = models.Schema.query.get(question.idSchema)
        conn = sqlite3.connect(schema.path)
        cur = conn.cursor()
        try:
            cur.execute(answer.sql)
            values = cur.fetchall()
            result = {'data': list(values), 'len': len(values)}
            if question.result is None:
                question.result = json.dumps(result)
            else:
                origin = json.loads(question.result)
                if origin != result:
                    return get_common_error_dic('result not match origin: %s your commit %s' % (question.result, json.dumps(result)))
        except Exception as e:
            return get_common_error_dic(str(e)), HTTP_Bad_Request
        finally:
            conn.close()
        db.session.add(answer)
        db.session.commit()
        return {}, HTTP_Created

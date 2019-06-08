from flask_restful import Resource, fields, marshal_with, marshal
import models
from exts import db
from common.comm import auth_admin, auth_all
from config import *
from flask import request
import moz_sql_parser
import json
import sqlite3
import sqlparse
from common.for_sqlite import gen_answer_sql_result, judge_schema_table_rows_empty
from common.segment import Segment
import math

answer_field = {
    'id': fields.Integer,
    'idQuestion': fields.Integer,
    'sql': fields.String,
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
            question = ret.Question
            db.session.delete(ret)
            db.session.commit()
            answer_left = models.Answer.query.filter_by(idQuestion=question.id).first()
            if answer_left is None:
                question.result = None
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
        answer.sql = request.json.get('sql')
        if answer.idQuestion is None or answer.sql is None:
            return get_shortage_error_dic("idQuestion data"), HTTP_Bad_Request
        if question is None:
            return get_common_error_dic("question id is wrong"), HTTP_Bad_Request
        if judge_schema_table_rows_empty(question.idSchema):
            return get_common_error_dic('schema table is empty!')
        try:
            answer.sql = ' '.join(sqlparse.format(answer.sql, keyword_case='upper').split())
            parsed = moz_sql_parser.parse(answer.sql)
            answer.json = json.dumps(parsed)
        except Exception as e:
            return get_except_error(e)
        # TODO: gen segmentation, gen result
        schema = models.Schema.query.get(question.idSchema)
        try:
            result = gen_answer_sql_result(schema, answer.sql)
            if question.result is None:
                question.result = json.dumps(result)
            else:
                origin = json.loads(question.result)
                if origin != result:
                    return get_common_error_dic(
                        'result not match origin: %s your commit %s' % (question.result, json.dumps(result)))
        except Exception as e:
            return get_common_error_dic(str(e)), HTTP_Bad_Request

        db.session.add(answer)
        db.session.commit()

        segment = Segment(answer.sql)
        segment_score = math.ceil(question.score/len(segment.segment_str))
        for idx,segment_str in enumerate(segment.segment_str):
            db_segment = models.Segmentation()
            db_segment.score = segment_score
            db_segment.data = segment_str
            db_segment.idAnswer = answer.id
            db_segment.rank = idx
            db.session.add(db_segment)
        db.session.commit()
        return {}, HTTP_Created

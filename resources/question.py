from flask_restful import Resource, fields, marshal_with, marshal
import models
from exts import db
from common.comm import auth_admin, auth_all
from config import *
from flask import request
import sqlite3

question_field = {
    'id': fields.Integer,
    'idSchema': fields.Integer,
    'title': fields.String,
    'text': fields.String,
    'score': fields.Integer,
    'result': fields.String
}


class Questions(Resource):

    @auth_all(False)
    @marshal_with(question_field)
    def get(self, question_id):
        ret = models.Question.query.filter_by(id=question_id).first()
        if ret is not None:
            return ret, HTTP_OK
        else:
            return {}, HTTP_NotFound

    @auth_admin(False)
    def delete(self, question_id):
        ret = models.Question.query.filter_by(id=question_id).first()
        if ret is not None:
            db.session.delete(ret)
            db.session.commit()
            return {}, HTTP_OK
        else:
            return {}, HTTP_NotFound

    @auth_admin(False)
    def patch(self, question_id):
        ret = models.Question.query.filter_by(id=question_id).first()
        if ret is not None:
            title = request.json.get('title')
            text = request.json.get('text')
            score = request.json.get('score')
            idSchema = request.json.get('idSchema')
            result = request.json.get('result')  # clear result
            ret.title = ret.title if title is None else title
            ret.text = ret.text if text is None else text
            ret.score = ret.score if score is None else score
            ret.idSchema = ret.idSchema if idSchema is None else idSchema
            ret.result = ret.result if result is None else None
            if idSchema is not None:
                schema = models.Schema.query.get(idSchema)
                answer = models.Answer.query.query.filter_by(idQuestion=ret.id).first()
                if schema is None:
                    return get_common_error_dic("can't find schema")
                # TODO: need to modify result
                if answer is not None:
                    conn = sqlite3.connect(schema.path)
                    cur = conn.cursor()
                    try:
                        pass
                    except Exception as e:
                        return get_common_error_dic(str(e)), HTTP_Bad_Request
                    finally:
                        conn.close()
            db.session.commit()
            return {}, HTTP_OK
        else:
            return {}, HTTP_NotFound


class QuestionList(Resource):

    @auth_all(inject=False)
    def get(self):
        questions = models.Question.query.filter_by()
        data = [marshal(q, question_field) for q in questions]
        return {'data': data}, HTTP_OK

    @auth_admin(inject=False)
    def post(self):
        q = models.Question()
        q.idSchema = request.json['idSchema']
        schema = models.Schema.query.get(q.idSchema)
        q.title = request.json['title']
        q.text = request.json['text']
        q.score = request.json['score']
        if q.idSchema is None or q.title is None or q.text is None or q.score is None:
            return get_shortage_error_dic("text title score"), HTTP_Bad_Request
        if schema is None:
            return get_common_error_dic("can't find schema")
        db.session.add(q)
        db.session.commit()
        return {}, HTTP_Created

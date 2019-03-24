from flask_restful import Resource, reqparse, abort, fields, marshal_with, marshal
import models
from exts import db
from common.comm import auth_admin
from config import *
from flask import request
import os
import sqlite3

student_fields = {
    'id': fields.String,
    'name': fields.String
}


class Students(Resource):

    method_decorators = [auth_admin(False)]

    @marshal_with(student_fields)
    def get(self, student_id):
        ret = models.Student.query.filter_by(id=student_id).first()
        if ret is not None:
            return ret, HTTP_OK
        else:
            return {}, HTTP_NotFound

    def delete(self, student_id):
        ret = models.Student.query.filter_by(id=student_id).first()
        if ret is not None:
            db.session.delete(ret)
            db.session.commit()
            return {}, HTTP_OK
        else:
            return {}, HTTP_NotFound


class StudentList(Resource):
    method_decorators = [auth_admin(inject=False)]

    def get(self):
        students = models.Student.query()
        data = [marshal(student, student_fields) for student in students]
        return {'data': data}, HTTP_OK

    def post(self):
        student = models.Student()
        student.id = request.json.get('id')
        student.password = request.json.get('password')
        student.name = request.json.get('name')
        if student.id is not None and student.password is not None:
            db.session.add(student)
            db.session.commit()
            return {}, HTTP_Created
        else:
            return get_shortage_error_dic('name id password'), HTTP_Bad_Request

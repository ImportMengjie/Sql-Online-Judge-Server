from flask_restful import Resource, reqparse, abort, fields, marshal_with, marshal
import models
from exts import db
from common.comm import auth_admin,auth_student
from config import *
from flask import request

student_fields = {
    'id': fields.String,
    'name': fields.String,
    'password': fields.String
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

    def put(self, student_id):
        ret = models.Student.query.filter_by(id=student_id).first()
        if ret is not None:
            ret.password = request.json['password']
            ret.name = request.json['name']
            try:
                db.session.commit()
            except Exception as e:
                return get_except_error(e)
            return {}, HTTP_OK
        else:
            return {}, HTTP_NotFound

    def patch(self, student_id):
        ret = models.Student.query.filter_by(id=student_id).first()
        if ret is not None:
            ret.password = ret.password if request.json['password'] is None else request.json['password']
            ret.name = ret.name if request.json['name'] is None else request.json['name']
            try:
                db.session.commit()
            except Exception as e:
                return get_except_error(e)
            return {}, HTTP_OK
        else:
            return {}, HTTP_NotFound


class StudentList(Resource):
    method_decorators = []

    @auth_admin(inject=False)
    def get(self):
        students = models.Student.query.filter_by()
        data = [marshal(student, student_fields) for student in students]
        return {'data': data}, HTTP_OK

    @auth_admin(inject=False)
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

    @auth_student()
    def patch(self, student):
        name = request.json['name']
        password = request.json['password']
        student.name = student.name if name is None else name
        student.password = student.password if password is None else password
        try:
            db.session.commit()
        except Exception as e:
            return get_except_error(e)
        return {}, HTTP_OK

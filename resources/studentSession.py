import hashlib
import os

from flask_restful import Resource, reqparse, abort
from models import Student
from exts import db
from common.comm import auth_student

student_login_parser = reqparse.RequestParser()
student_login_parser.add_argument('username', location='json')
student_login_parser.add_argument('password', location='json')


class StudentSession(Resource):

    @auth_student
    def get(self, student):
        return {'name': student.name,'id':student.id}, 200

    def post(self):
        args = student_login_parser.parse_args()
        ret = Student.query.filter_by(id=args["username"], password=args["password"])
        if ret is not None and ret.first() is not None:
            student = ret.first()
            student_session = hashlib.sha1(os.urandom(24)).hexdigest()
            student.session= student_session
            db.session.commit()
            return {"session": student_session, 'name':student.name}, 201
        abort(401)

    @auth_student
    def delete(self, student):
        student.session = None
        db.session.commit()
        return {}, 200

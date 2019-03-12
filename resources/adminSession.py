from flask import request
from flask_restful import Resource, reqparse
from exts import db
from models import Student

admin_login_parser = reqparse.RequestParser()
admin_login_parser.add_argument('username', location='json')
admin_login_parser.add_argument('password', location='json')


class AdminSession(Resource):

    def get(self):
        pass

    def post(self):
        args = admin_login_parser.parse_args()
        json = request.get_json()
        s = Student(id=args['username'], password=args['password'], name='王二狗')
        # db.insert(s)
        db.session.add(s)
        db.session.commit()
        print(json)
        return args

    def delete(self):
        pass

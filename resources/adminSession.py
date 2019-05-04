import hashlib
import os

from flask_restful import Resource, reqparse, abort
from models import Admin
from exts import db
from common.comm import auth_admin

admin_login_parser = reqparse.RequestParser()
admin_login_parser.add_argument('username', location='json')
admin_login_parser.add_argument('password', location='json')


class AdminSession(Resource):

    @auth_admin
    def get(self, admin):
        return {'name': admin.name}, 200

    def post(self):
        args = admin_login_parser.parse_args()
        ret = Admin.query.filter_by(name=args["username"], password=args["password"])
        if ret is not None and ret.first() is not None:
            admin = ret.first()
            admin_session = hashlib.sha1(os.urandom(24)).hexdigest()
            admin.session = admin_session
            db.session.commit()
            return {"session": admin_session, "name":admin.name}, 201
        abort(401)

    @auth_admin
    def delete(self, admin):
        print(admin.password)
        print(admin.name)
        admin.session = None
        db.session.commit()
        return {}, 200

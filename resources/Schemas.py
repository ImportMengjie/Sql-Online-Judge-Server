from flask_restful import Resource, reqparse, abort, fields, marshal_with
import models
from exts import db
from common.comm import auth_admin
from config import *

schema_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String
}


class Schema(Resource):
    method_decorators = [auth_admin]

    @marshal_with(schema_fields)
    def get(self, schema_id, admin):
        ret = models.Schema.query.filter_by(id=schema_id).first()
        if ret is not None:
            return ret, HTTP_OK
        else:
            return '', HTTP_NotFound

    def delete(self, schema_id,admin):
        ret = models.Schema.query.filter_by(id=schema_id).first()
        if ret is not None:
            db.session.delete(ret)
            db.session.commit()
            return '', HTTP_OK
        else:
            return '', HTTP_NotFound


class SchemaList(Resource):
    method_decorators = [auth_admin]

    @auth_admin
    def get(self):
        pass

    @auth_admin
    def post(self):
        pass

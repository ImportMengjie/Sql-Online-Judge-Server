from flask_restful import Resource, reqparse, abort, fields, marshal_with, marshal
import models
from exts import db
from common.comm import auth_admin,auth_all
from config import *
from flask import request
import os
import sqlite3
import json

schema_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
    'keywords': fields.String
}


class Schema(Resource):

    @auth_all(inject=False)
    @marshal_with(schema_fields)
    def get(self, schema_id):
        ret = models.Schema.query.filter_by(id=schema_id).first()
        if ret is not None:
            return ret, HTTP_OK
        else:
            return {}, HTTP_NotFound

    @auth_admin(inject=False)
    def delete(self, schema_id):
        ret = models.Schema.query.filter_by(id=schema_id).first()
        if ret is not None:
            os.remove(ret.path)
            db.session.delete(ret)
            db.session.commit()
            return {}, HTTP_OK
        else:
            return {}, HTTP_NotFound


class SchemaList(Resource):

    @auth_all(inject=False)
    def get(self):
        schemas = models.Schema.query.filter_by()
        data = [marshal(schema,schema_fields) for schema in schemas]
        return {'data':data}, HTTP_OK

    @auth_admin(inject=False)
    def post(self):
        schema = models.Schema()
        schema.name = request.json.get('name')
        schema.description = request.json.get('description')
        schema.keywords = schema.name
        if schema.name is not None:
            schema.path = os.path.join(save_db_path,schema.name+'.db')
            db.session.add(schema)
            db.session.commit()
            conn = sqlite3.connect(schema.path)
            conn.close()
            return {}, HTTP_Created
        else:
            return get_shortage_error_dic('name'), HTTP_Bad_Request

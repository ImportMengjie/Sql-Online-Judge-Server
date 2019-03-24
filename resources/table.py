from flask_restful import Resource, reqparse, abort, fields, marshal_with, marshal
import models
from exts import db
from common.comm import auth_admin
from config import *
from flask import request
import sqlite3

table_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'idSchema': fields.Integer,
    'sql': fields.String,
    'description': fields.String
}


class Table(Resource):
    method_decorators = [auth_admin(False)]

    @marshal_with(table_fields)
    def get(self, idSchema, table_id):
        ret = models.Table.query.filter_by(id=table_id).first()
        if ret is not None:
            if idSchema != ret.idSchema:
                return ret, HTTP_Bad_Request
            return ret, HTTP_OK
        else:
            return {}, HTTP_NotFound

    def delete(self, idSchema, table_id):
        ret = models.Schema.query.filter_by(id=table_id).first()
        if ret is not None:
            if ret.idSchema != idSchema:
                return get_common_error_dic('schema id not match table id'), HTTP_Bad_Request
            db.session.delete(ret)
            db.session.commit()
            return {}, HTTP_OK
        else:
            return {}, HTTP_NotFound


class TableList(Resource):
    method_decorators = [auth_admin(inject=False)]

    def get(self, idSchema):
        tables = models.Table.query.filter_by(idSchema=idSchema)
        data = [marshal(table, table_fields) for table in tables]
        return {'data': data}, HTTP_OK

    def post(self, idSchema):
        table = models.Table()
        table.name = request.json.get('name')
        table.sql = request.json.get('sql')
        table.idSchema = idSchema
        table.description = request.json.get('description')
        schema = models.Schema.query.get(idSchema)
        if table.name is not None and table.sql is not None and schema is not None:
            conn = sqlite3.connect(schema.path)
            c = conn.cursor()
            try:
                c.execute(table.sql)
                conn.commit()
            except Exception as e:
                return get_common_error_dic(str(e)), HTTP_Bad_Request
            finally:
                conn.close()
            db.session.add(table)
            db.session.commit()
            return {}, HTTP_Created
        else:
            return get_shortage_error_dic('name or idSchema or sql'), HTTP_Bad_Request

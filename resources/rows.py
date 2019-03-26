from flask_restful import Resource, reqparse, abort, fields, marshal_with, marshal
import models
from exts import db
from common.comm import auth_admin
from config import *
from flask import request
import os
import sqlite3

rows_fields = {
    'id': fields.Integer,
    'idTable': fields.String,
    'sql': fields.String
}


class Rows(Resource):

    method_decorators = [auth_admin(False)]

    @marshal_with(rows_fields)
    def get(self, idTable, rows_id):
        ret = models.Insert.query.filter_by(id=rows_id).first()
        if ret is not None:
            if idTable != ret.idTable:
                return ret, HTTP_Bad_Request
            return ret, HTTP_OK
        else:
            return {}, HTTP_NotFound

    def delete(self, idTable, rows_id):
        ret = models.Insert.query.filter_by(id=rows_id).first()
        if ret is not None:
            if ret.idTable != idTable:
                return get_common_error_dic('table id not match rows id'), HTTP_Bad_Request
            db.session.delete(ret)
            db.session.commit()
            return {}, HTTP_OK
        else:
            return {}, HTTP_NotFound


class RowsList(Resource):
    method_decorators = [auth_admin(inject=False)]

    def get(self, idTable):
        rows = models.Insert.query.filter_by(idTable=idTable)
        data = [marshal(row, rows_fields) for row in rows]
        return {'data': data}, HTTP_OK

    def post(self, idTable):
        row = models.Insert()
        row.idTable = idTable
        row.sql = request.json.get('sql')
        table = models.Table.query.get(idTable)
        schema = table.Schema
        if schema is not None and row.sql is not None:
            conn = sqlite3.connect(schema.path)
            c = conn.cursor()
            try:
                c.execute(row.sql)
                conn.commit()
            except Exception as e:
                return get_common_error_dic(str(e)), HTTP_Bad_Request
            finally:
                conn.close()
            db.session.add(row)
            db.session.commit()
            return {}, HTTP_Created
        else:
            return get_shortage_error_dic('idTable or sql'), HTTP_Bad_Request
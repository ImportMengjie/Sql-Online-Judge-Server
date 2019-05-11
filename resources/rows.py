from flask_restful import Resource, reqparse, abort, fields, marshal_with, marshal
import models
from exts import db
from common.comm import auth_admin
from config import *
from flask import request
import os
import sqlite3
from common.for_question import update_result

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
            schema = ret.Table.Schema
            db.session.delete(ret)
            db.session.commit()
            update_result(schema)
            return {}, HTTP_OK
        else:
            return {}, HTTP_NotFound


class RowsList(Resource):
    method_decorators = [auth_admin(inject=False)]

    def get(self, idTable):
        rows = models.Insert.query.filter_by(idTable=idTable)
        data = [marshal(row, rows_fields) for row in rows]
        table = models.Table.query.get(idTable)
        schema = table.Schema
        ret = {}
        if schema is not None:
            conn = sqlite3.connect(schema.path)
            c = conn.cursor()
            try:
                c.execute('select * from ' + table.name)
                ret = c.fetchall()
                print(c.fetchall())
            except Exception as e:
                return get_common_error_dic(str(e)), HTTP_Bad_Request
            finally:
                conn.close()

        return {'data': data, 'detail': ret}, HTTP_OK

    # DONE need to update answer result
    def post(self, idTable):
        row = models.Insert()
        row.idTable = idTable
        row.sql = request.json.get('sql')
        data = request.json.get('data')
        table = models.Table.query.get(idTable)
        if data is not None and row.sql is None:
            row.sql='INSERT INTO '+table.name+' VALUES'+str(tuple(data))
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
            update_result(schema)
            return {}, HTTP_Created
        else:
            return get_shortage_error_dic('idTable or sql'), HTTP_Bad_Request

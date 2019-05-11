from flask_restful import Resource, reqparse, abort, fields, marshal_with, marshal
import models
from exts import db
from common.comm import auth_admin, auth_all
from common.for_sqlite import recover_schema
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
        ret = models.Table.query.filter_by(id=table_id).first()

        if ret is not None:
            # delete table in sqlite
            recover_schema(ret.Schema)
            conn = sqlite3.connect(ret.Schema.path)
            cur = conn.cursor()
            try:
                cur.execute('DROP TABLE IF EXISTS {}'.format(ret.name))
            except Exception as e:
                return get_common_error_dic(str(e)), HTTP_Server_Error
            finally:
                cur.close()
                conn.close()

            if ret.idSchema != idSchema:
                return get_common_error_dic('schema id not match table id'), HTTP_Bad_Request
            db.session.delete(ret)
            db.session.commit()
            return {}, HTTP_OK
        else:
            return {}, HTTP_NotFound


class TableList(Resource):

    @auth_all(inject=True)
    def get(self, idSchema, student, admin):
        tables = models.Table.query.filter_by(idSchema=idSchema)
        schema = models.Schema.query.get(idSchema)
        if schema is None:
            abort(404)
        recover_schema(schema)
        ret = {'table_name': [], 'table': {}}
        conn = sqlite3.connect(schema.path)
        cur = conn.cursor()
        try:
            for table in tables:
                ret['table'][table.name] = {'description': table.description}
                ret['table_name'].append(table.name)
                cur.execute('PRAGMA table_info({})'.format(table.name))
                table_col = cur.fetchall()
                ret['table'][table.name]['cols'] = table_col
        except Exception as e:
            return get_common_error_dic(str(e)), HTTP_Bad_Request
        finally:
            cur.close()
            conn.close()

        if admin is not None:
            data = [marshal(table, table_fields) for table in tables]
            ret['data']=data
            return ret, HTTP_OK
        else:
            return ret

    @auth_admin(inject=False)
    def post(self, idSchema):
        table = models.Table()
        table.name = request.json.get('name')
        table.sql = request.json.get('sql')
        # DONE parse to extra table name
        if table.name is None:
            name = table.sql.split()[2]
            table.name=name[:name.index('(') if '(' in name else None]

        table.idSchema = idSchema
        table.description = request.json.get('description')
        schema = models.Schema.query.get(idSchema)
        if table.name is not None and table.sql is not None and schema is not None:
            recover_schema(schema)

            conn = sqlite3.connect(schema.path)
            cur = conn.cursor()
            try:
                cur.execute(table.sql)
                conn.commit()
                cur.close()
                cur = conn.cursor()
                cur.execute('PRAGMA table_info({})'.format(table.name))
                keywords = schema.keywords.split(' ')
                ret = cur.fetchall()
                for r in ret:
                    if r[1] not in keywords:
                        keywords.append(r[1])
                if table.name not in keywords:
                    keywords.append(table.name)
                schema.keywords = ' '.join(keywords)
                db.session.commit()
                cur.close()
            except Exception as e:
                return get_common_error_dic(str(e)), HTTP_Bad_Request
            finally:
                conn.close()
            db.session.add(table)
            db.session.commit()
            return {}, HTTP_Created
        else:
            return get_shortage_error_dic('name or idSchema or sql'), HTTP_Bad_Request

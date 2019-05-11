import models
import os
import sqlite3
import json


def recover_schema(schema: models.Schema, overwrite=False):
    if overwrite and os.path.exists(schema.path):
        os.remove(schema.path)
    if not os.path.exists(schema.path) or overwrite:
        conn = sqlite3.connect(schema.path)
        cur = conn.cursor()
        tables = models.Table.query.filter_by(idSchema=schema.id)
        for t in tables:
            cur.execute(t.sql)
            for r in models.Insert.query.filter_by(idTable=t.id).order_by(models.Insert.id):
                cur.execute(r.sql)
            conn.commit()
        cur.close()
        conn.close()


def gen_answer_sql_result(schema: models.Schema, sql: str):
    recover_schema(schema)
    conn = sqlite3.connect(schema.path)
    cur = conn.cursor()
    try:
        cur.execute(sql)
        values = cur.fetchall()
        result = {'data': list(values), 'len': len(values)}
    except Exception as e:
        raise e
    finally:
        cur.close()
        conn.close()
    return json.loads(json.dumps(result))

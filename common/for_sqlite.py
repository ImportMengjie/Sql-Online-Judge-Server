import models
import os
import sqlite3


def recover_schema(schema: models.Schema):
    if not os.path.exists(schema.path):
        conn = sqlite3.connect(schema.path)
        cur = conn.cursor()
        tables = models.Table.query.filter_by(idSchema=schema.id)
        for t in tables:
            cur.execute(t.sql)
            for r in models.Insert.query.filter_by(idTable=t.id):
                cur.execute(r.sql)
            conn.commit()
        cur.close()
        conn.close()

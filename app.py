from flask import Flask
from flask_restful import Api
from exts import db
from resources.adminSession import AdminSession
from resources.studentSession import StudentSession
from resources.Schemas import Schema, SchemaList

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/sql_judge'
db.init_app(app)


@app.route('/')
def hello_world():
    return 'Hello World!'


api.add_resource(AdminSession, '/admin/session')
api.add_resource(StudentSession, '/student/session')
api.add_resource(Schema, '/schema/<int:schema_id>')
api.add_resource(SchemaList, '/schema')

if __name__ == '__main__':
    app.run(debug=True)

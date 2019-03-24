from flask import Flask
from flask_restful import Api
from exts import db
from resources.adminSession import AdminSession
from resources.studentSession import StudentSession
from resources.schemas import Schema, SchemaList
from resources.table import Table, TableList
from resources.rows import Rows, RowsList
from resources.students import StudentList, Students
import config

app = Flask(__name__)
api = Api(app, errors=config.errors)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/sql_judge'
db.init_app(app)


@app.route('/')
def hello_world():
    return 'Hello World!'


api.add_resource(Students, '/student/<string:student_id>')
api.add_resource(StudentList, '/student')

api.add_resource(AdminSession, '/session/admin')
api.add_resource(StudentSession, '/session/student')

api.add_resource(Schema, '/schema/<int:schema_id>')
api.add_resource(SchemaList, '/schema')

api.add_resource(Table, '/schema/<int:idSchema>/table/<int:table_id>')
api.add_resource(TableList, '/schema/<int:idSchema>/table')

api.add_resource(Rows, '/table/<int:idTable>/rows/<int:rows_id>')
api.add_resource(RowsList, '/table/<int:idTable>/rows')

if __name__ == '__main__':
    app.run(debug=True)

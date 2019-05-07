from flask import Flask
from flask_restful import Api
import flask_cors
from exts import db
from resources.adminSession import AdminSession
from resources.studentSession import StudentSession
from resources.schemas import Schema, SchemaList
from resources.table import Table, TableList
from resources.rows import Rows, RowsList
from resources.students import StudentList, Students
from resources.question import QuestionList, Questions
from resources.answer import AnswerList, Answers
from resources.segmentation import Segmentation, SegmentationList
from resources.submit import SubmitList, Submits

import config

app = Flask(__name__)
api = Api(app, errors=config.errors)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/sql_online_judge'
db.init_app(app)
flask_cors.CORS(app)

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

api.add_resource(Questions, '/question/<int:question_id>')
api.add_resource(QuestionList, '/question')

api.add_resource(Answers, '/question/<int:idQuestion>/answer/<int:answer_id>')
api.add_resource(AnswerList, '/question/<int:idQuestion>/answer')

api.add_resource(Segmentation, '/answer/<int:idAnswer>/segment/<int:segmentation_id>')
api.add_resource(SegmentationList, '/answer/<int:idAnswer>/segment')

api.add_resource(Submits, '/student/<int:idStudent>/submit/<int:submit_id>')
api.add_resource(SubmitList, '/student/<int:idStudent>/submit', '/question/<int:idQuestion>/submit',
                 '/question/<int:idQuestion>/student/<int:idStudent>/submit')


if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, jsonify, request
from flask_restful import Api, Resource, reqparse
from exts import db
from resources.adminSession import AdminSession


app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/sql_judge'
db.init_app(app)

@app.route('/')
def hello_world():
    return 'Hello World!'

api.add_resource(AdminSession, '/hello')

if __name__ == '__main__':
    app.run(debug=True)

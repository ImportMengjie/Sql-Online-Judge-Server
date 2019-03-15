from flask import request
from functools import wraps
from models import Admin,Student
from flask_restful import abort


def auth_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        session = request.json.get('session')
        if session is None:
            abort(400)
        ret = Admin.query.filter_by(session=session).first()
        if ret is None:
            abort(401)
        return func(admin=ret, *args, **kwargs)

    return wrapper


def auth_student(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        session = request.json.get('session')
        if session is None:
            abort(400)
        ret = Student.query.filter_by(session=session).first()
        if ret is None:
            abort(401)
        return func(student=ret, *args, **kwargs)

    return wrapper


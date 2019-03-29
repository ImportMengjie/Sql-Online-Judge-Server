from flask import request
from functools import wraps
from models import Admin, Student
from flask_restful import abort


def auth_admin(inject=True):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            session = None
            if request.method == 'GET':
                session = request.headers.get('session')
            elif request.json is not None:
                session = request.json.get('session')
            if session is None:
                abort(400)
            ret = Admin.query.filter_by(session=session).first()
            if ret is None:
                abort(401)
            if inject:
                return func(admin=ret, *args, **kwargs)
            else:
                return func(*args, **kwargs)

        return wrapper

    return decorator


def auth_student(inject=True):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            session = None
            if request.method == 'GET':
                session = request.headers.get('session')
            elif request.json is not None:
                session = request.json.get('session')
            if session is None:
                abort(400)
            ret = Student.query.filter_by(session=session).first()
            if ret is None:
                abort(401)
            if inject:
                return func(student=ret, *args, **kwargs)
            else:
                return func(*args, **kwargs)

        return wrapper

    return decorator


def auth_all(inject=True):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            session = None
            if request.method == 'GET':
                session = request.headers.get('session')
            elif request.json is not None:
                session = request.json.get('session')
            if session is None:
                abort(400)
            ret_student = Student.query.filter_by(session=session).first()
            ret_admin = Admin.query.filter_by(session=session).first()
            if ret_admin is None and ret_student is None:
                abort(401)
            if inject:
                return func(student=ret_student, admin=ret_admin, *args, **kwargs)
            else:
                return func(*args, **kwargs)

        return wrapper

    return decorator

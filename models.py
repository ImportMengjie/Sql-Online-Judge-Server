# coding: utf-8
from sqlalchemy import ForeignKey, String, TIMESTAMP, Text, text
from sqlalchemy.dialects.mysql import INTEGER
from exts import db


class Admin(db.Model):
    __tablename__ = 'Admin'

    name = db.Column(db.String(30), primary_key=True, unique=True)
    password = db.Column(db.String(45), nullable=False)
    session = db.Column(db.String(128), unique=True)
    extra = db.Column(db.String(500))


class Schema(db.Model):
    __tablename__ = 'Schema'

    id = db.Column(INTEGER(11), primary_key=True, unique=True)
    name = db.Column(db.String(45), nullable=False)
    path = db.Column(db.String(200), nullable=False, unique=True)
    keywords = db.Column(db.String(10000), nullable=False,)
    description = db.Column(db.String(1000))


class Student(db.Model):
    __tablename__ = 'Student'

    id = db.Column(db.String(15), primary_key=True, unique=True)
    password = db.Column(db.String(20), nullable=False)
    session = db.Column(db.String(128), unique=True)
    name = db.Column(db.String(16))


class Question(db.Model):
    __tablename__ = 'Question'

    id = db.Column(INTEGER(11), primary_key=True, unique=True)
    idSchema = db.Column(db.ForeignKey('Schema.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(1000), nullable=False)
    text = db.Column(db.String(5000), nullable=False)
    score = db.Column(INTEGER(11), nullable=False, server_default=db.text("'5'"))
    result = db.Column(String(10000), nullable=True)

    Schema = db.relationship('Schema')


class Table(db.Model):
    __tablename__ = 'Table'

    id = db.Column(INTEGER(11), primary_key=True)
    name = db.Column(String(45))
    idSchema = db.Column(ForeignKey('Schema.id', ondelete='CASCADE'), nullable=False, index=True)
    sql = db.Column(String(500), nullable=False)
    description = db.Column(db.String(1000))

    Schema = db.relationship('Schema')


class Answer(db.Model):
    __tablename__ = 'Answer'

    id = db.Column(INTEGER(11), primary_key=True)
    idQuestion = db.Column(ForeignKey('Question.id', ondelete='CASCADE'), nullable=False, index=True)
    sql = db.Column(String(400), nullable=False)
    json = db.Column(String(600))

    Question = db.relationship('Question')


class Insert(db.Model):
    __tablename__ = 'Insert'

    id = db.Column(INTEGER(11), primary_key=True)
    idTable = db.Column(ForeignKey('Table.id'), nullable=False, index=True)
    sql = db.Column(String(500), nullable=False)

    Table = db.relationship('Table')


class Submit(db.Model):
    __tablename__ = 'Submit'

    id = db.Column(INTEGER(11), primary_key=True)
    idStudent = db.Column(ForeignKey('Student.id'), nullable=False, index=True)
    idQuestion = db.Column(ForeignKey('Question.id', ondelete='CASCADE'), nullable=False, index=True)
    idAnswer = db.Column(ForeignKey('Answer.id', ondelete='CASCADE'), nullable=False, index=True)
    score = db.Column(INTEGER(11), nullable=False)
    answer = db.Column(String(300), nullable=False)
    correct = db.Column(String(300), nullable=False)
    segmentJson = db.Column(String(5000), nullable=False)
    spelling = db.Column(INTEGER(11), nullable=False)
    type = db.Column(INTEGER(11), nullable=False)
    result = db.Column(String(5000), nullable=False)
    time = db.Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    info = db.Column(String(500))

    Question = db.relationship('Question')
    Student = db.relationship('Student')
    Answer = db.relationship('Answer')


class Segmentation(db.Model):
    __tablename__ = 'Segmentation'

    id = db.Column(INTEGER(11), primary_key=True)
    idAnswer = db.Column(ForeignKey('Answer.id', ondelete='CASCADE'), nullable=False, index=True)
    rank = db.Column(INTEGER(11), nullable=False)
    score = db.Column(INTEGER(11), nullable=False)
    data = db.Column(Text, nullable=False)
    extra = db.Column(Text)

    Answer = db.relationship('Answer')

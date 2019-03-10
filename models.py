# coding: utf-8
from sqlalchemy import Column, ForeignKey, String, TIMESTAMP, Text, text
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Schema(Base):
    __tablename__ = 'Schema'

    id = Column(INTEGER(11), primary_key=True)
    path = Column(String(200), nullable=False, unique=True)


class Student(Base):
    __tablename__ = 'Student'

    id = Column(String(15), primary_key=True, unique=True)
    password = Column(String(20), nullable=False)
    session = Column(String(128), unique=True)
    name = Column(String(16))


class Question(Base):
    __tablename__ = 'Question'

    id = Column(INTEGER(11), primary_key=True, unique=True)
    idSchema = Column(ForeignKey('Schema.id', ondelete='CASCADE'), nullable=False, index=True)
    title = Column(String(1000), nullable=False)
    text = Column(String(5000), nullable=False)
    score = Column(INTEGER(11), nullable=False, server_default=text("'5'"))
    result = Column(String(10000), nullable=False)

    Schema = relationship('Schema')


class Table(Base):
    __tablename__ = 'Table'

    id = Column(INTEGER(11), primary_key=True)
    idSchema = Column(ForeignKey('Schema.id', ondelete='CASCADE'), nullable=False, index=True)
    sql = Column(String(500), nullable=False)

    Schema = relationship('Schema')


class Answer(Base):
    __tablename__ = 'Answer'

    id = Column(INTEGER(11), primary_key=True)
    idQuestion = Column(ForeignKey('Question.id', ondelete='CASCADE'), nullable=False, index=True)
    data = Column(String(400), nullable=False)
    json = Column(String(600))

    Question = relationship('Question')


class Insert(Base):
    __tablename__ = 'Insert'

    id = Column(INTEGER(11), primary_key=True)
    idTable = Column(ForeignKey('Table.id'), nullable=False, index=True)
    sql = Column(String(500), nullable=False)

    Table = relationship('Table')


class Submit(Base):
    __tablename__ = 'Submit'

    id = Column(INTEGER(11), primary_key=True)
    idStudent = Column(ForeignKey('Student.id'), nullable=False, index=True)
    idQuestion = Column(ForeignKey('Question.id', ondelete='CASCADE'), nullable=False, index=True)
    score = Column(INTEGER(11), nullable=False)
    answer = Column(String(300), nullable=False)
    time = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    Question = relationship('Question')
    Student = relationship('Student')


class Segmentation(Base):
    __tablename__ = 'Segmentation'

    id = Column(INTEGER(11), primary_key=True)
    idAnswer = Column(ForeignKey('Answer.id', ondelete='CASCADE'), nullable=False, index=True)
    rank = Column(INTEGER(11), nullable=False)
    score = Column(INTEGER(11), nullable=False)
    data = Column(Text, nullable=False)
    extra = Column(Text)

    Answer = relationship('Answer')

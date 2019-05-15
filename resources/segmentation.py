from flask_restful import Resource, fields, marshal_with, marshal
import models
from exts import db
from common.comm import auth_admin, auth_all
from config import *
from flask import request

segmentation_field = {
    'id': fields.Integer,
    'idAnswer': fields.Integer,
    'rank': fields.Integer,
    'score': fields.Integer,
    'data': fields.String,
    'extra': fields.String,
}


class Segmentation(Resource):

    @auth_all(False)
    @marshal_with(segmentation_field)
    def get(self, idAnswer, segmentation_id):
        ret = models.Segmentation.query.filter_by(id=segmentation_id).first()
        if ret is not None:
            return ret, HTTP_OK
        else:
            return {}, HTTP_NotFound

    @auth_admin(False)
    def patch(self, idAnswer, segmentation_id):
        ret = models.Segmentation.query.filter_by(id=segmentation_id).first()
        if ret is not None:
            score = request.json.get('score')
            extra = request.json.get('extra')
            data = request.json.get('data')
            ret.score = ret.score if score is None else score
            ret.extra = ret.extra if extra is None else extra
            ret.data = ret.data if data is None else data
            db.session.commit()
        else:
            return {}, HTTP_NotFound


class SegmentationList(Resource):

    @auth_all(inject=False)
    def get(self, idAnswer):
        segments = models.Segmentation.query.filter_by(idAnswer=idAnswer).order_by(models.Segmentation.rank)
        data = [marshal(s, segmentation_field) for s in segments]
        return {'data': data}, HTTP_OK


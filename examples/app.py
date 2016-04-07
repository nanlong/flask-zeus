# encoding:utf-8
from __future__ import unicode_literals
from __future__ import absolute_import
from flask import Flask, Blueprint
from flask_zeus.model import db, CRUDMixin
from flask_zeus.user import AccountMixin
from flask_zeus.api import ModelResource
from flask_restful import Api, fields

app = Flask(__name__)
app.config.from_object({
    'DEBUG': True
})

db.init_app(app)

api_bp = Blueprint('api_bp', __name__)
api = Api(api_bp)


class User(db.Model, CRUDMixin, AccountMixin):
    pass


user_fields = {
    'id': fields.Integer,
    'email': fields.String,
    'created_at': fields.DateTime(dt_format=b'iso8601'),
    'updated_at': fields.DateTime(dt_format=b'iso8601'),
    'token': fields.String(attribute=lambda x: x.token)
}


@api.resource('/users/', '/users/<id>/')
class UserRestful(ModelResource):
    model = User
    output_fields = user_fields


if __name__ == '__main__':
    app.run()




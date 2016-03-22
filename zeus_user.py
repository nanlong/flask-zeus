# encoding:utf-8
from __future__ import unicode_literals
from __future__ import absolute_import
from werkzeug.security import generate_password_hash, check_password_hash
from .zeus_model import db


class AccountMixin(object):

    email = db.Column('email', db.VARCHAR(255), index=True, unique=True)
    password_hash = db.Column('password_hash', db.VARCHAR(512))
    token = db.Column('token', db.VARCHAR(512), index=True, unique=True)

    @property
    def password(self):
        raise ValueError('no password')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def get_by_token(cls, token):
        return cls.query.filter_by(token=token).first()

    @classmethod
    def get_by_login(cls, username, password):
        user = cls.query.filter_by(email=username).first()
        if user and user.verify_password(password):
            return user

    def set_token(self):
        from itsdangerous import URLSafeSerializer as Serializer
        from flask import current_app
        serializer = Serializer(current_app.config.get('SECRET_KEY'))
        data = {'email': self.email, 'password': self.password_hash}
        self.token = serializer.dumps(data)

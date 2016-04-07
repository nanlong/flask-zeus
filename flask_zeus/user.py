# encoding:utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from flask import current_app
from itsdangerous import URLSafeSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.declarative import declared_attr
from .model import db


class AccountMixin(object):

    @declared_attr
    def email(self):
        return db.Column('email', db.VARCHAR(255), index=True, unique=True, doc='用户邮箱,用来做登陆帐号')

    @declared_attr
    def password_hash(self):
        return db.Column('password_hash', db.VARCHAR(512), doc='用户密码的hash值')

    @declared_attr
    def token(self):
        return db.Column('token', db.VARCHAR(512), index=True, unique=True, doc='用户token,通过邮箱和密码生成,唯一')

    @property
    def password(self):
        raise ValueError('no password')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def get_by_token(cls, token, _=None):
        return cls.query.filter_by(token=token).first()

    @classmethod
    def get_by_account(cls, username, password):
        user = cls.query.filter_by(email=username).first()
        if user and user.verify_password(password):
            return user

    def set_token(self):
        serializer = Serializer(current_app.config.get('SECRET_KEY'))
        data = {'email': self.email, 'password': self.password_hash}
        self.token = serializer.dumps(data)

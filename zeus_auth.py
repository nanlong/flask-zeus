# encoding:utf-8
from __future__ import unicode_literals
from __future__ import absolute_import
"""
需要为g对象 设置用户模型
example:
    @app.before_request
    def before_request():
        g.User = User
"""
from flask import g, request
from werkzeug.local import LocalProxy
from flask.ext.httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth('Token')
multi_auth = MultiAuth(basic_auth, token_auth)


class AnonymousUserMixin(object):
    """This is the default object for representing an anonymous user.
    """
    @property
    def is_authenticated(self):
        return False

    @property
    def is_active(self):
        return False

    @property
    def is_anonymous(self):
        return True

    def get_id(self):
        return


@basic_auth.verify_password
def verify_password(username, password):
    g.current_user = AnonymousUserMixin()
    user = g.User.get_by_login(username, password)
    if user:
        g.current_user = user
        return True
    return False


@token_auth.verify_token
def verify_token(token):
    g.current_user = AnonymousUserMixin()
    user = g.User.get_by_token(token)
    if user:
        g.current_user = user
        return True
    return False


def get_current_user():
    current_user = getattr(g, 'current_user', None)
    if current_user:
        return g.current_user

    username = request.authorization.get('username')
    password = request.authorization.get('password')

    if password:
        user = g.User.get_by_login(username, password)
    else:
        user = g.User.get_by_token(username)

    if user:
        return user
    return AnonymousUserMixin()


api_current_user = LocalProxy(lambda: get_current_user())

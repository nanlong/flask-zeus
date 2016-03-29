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
from flask.ext.login import AnonymousUserMixin

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth('Token')
multi_auth = MultiAuth(basic_auth, token_auth)


@basic_auth.verify_password
def verify_password(username, password):
    g.current_user = AnonymousUserMixin()
    user = g.User.get_by_account(username, password)
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

    if not current_user:
        username = request.authorization.get('username')
        password = request.authorization.get('password')
        get_user_method = [g.User.get_by_token, g.User.get_by_account][password]
        current_user = get_user_method(username, password)

    if not current_user:
        current_user = AnonymousUserMixin()

    return current_user


api_current_user = LocalProxy(lambda: get_current_user())

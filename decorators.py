# encoding:utf-8
from __future__ import unicode_literals
from __future__ import absolute_import
from functools import wraps
from flask import request, current_app


def jsonp(f):
    """Wraps JSONified output for JSONP requests."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            data = str(f(*args, **kwargs).data)
            content = str(callback) + '(' + data + ')'
            mime_type = 'application/javascript'
            return current_app.response_class(content, mimetype=mime_type)
        else:
            return f(*args, **kwargs)
    return decorated_function

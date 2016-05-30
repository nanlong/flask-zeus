# encoding:utf-8
from __future__ import unicode_literals
from __future__ import absolute_import
from flask import request
from flask.ext.wtf import Form as BaseForm
from wtforms_json import flatten_json
import werkzeug.datastructures
from flask_wtf.form import _Auto


class Form(BaseForm):

    def __init__(self, formdata=_Auto, *args, **kwargs):
        kwargs['csrf_enabled'] = False

        if formdata is _Auto and self.is_submitted() and request.json:
            formdata = flatten_json(self.__class__, request.json)
            formdata = werkzeug.datastructures.MultiDict(formdata)

        super(Form, self).__init__(formdata, *args, **kwargs)

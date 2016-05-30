# encoding:utf-8
from __future__ import unicode_literals
from __future__ import absolute_import
from flask import Blueprint as BaseBlueprint
import types


class Blueprint(BaseBlueprint):

    def route(self, rule, **options):

        def decorator(f):
            endpoint = options.pop('endpoint', f.__name__)

            view_func = f

            if not isinstance(f, types.FunctionType):
                class_args = options.pop('class_args', [])
                class_kwargs = options.pop('class_kwargs', {})
                view_func = f.as_view(endpoint.encode('utf-8'), *class_args, **class_kwargs)

            self.add_url_rule(rule, endpoint, view_func, **options)
            return f

        return decorator

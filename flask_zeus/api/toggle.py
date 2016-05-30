# encoding:utf-8
from __future__ import unicode_literals
from __future__ import absolute_import
from flask_restful import (Resource, marshal)
from flask_login import (login_required, current_user)
from .base import BaseResource
from .error import *


class ToggleResource(BaseResource, Resource):
    model = None
    output_fields = None

    @login_required
    def post(self, **kwargs):
        self.check_model()
        self.check_output_fields()

        if not self.model.has_property('user_id'):
            raise ZeusMethodNotAllowed

        stmt = self.generate_stmt(**kwargs)
        item = stmt.first()

        if not item:
            item = self.model()
            for k, v in kwargs.iteritems():
                if self.model.has_property(k):
                    setattr(item, k, v)
            item.user_id = current_user.id
            item.save()
            return marshal(item, self.output_fields), 201

        else:
            item.delete()
            return {}, 204

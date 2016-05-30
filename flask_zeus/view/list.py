# encoding:utf-8
from __future__ import unicode_literals
from __future__ import absolute_import
from flask_login import (login_required, current_user)
from .base import BaseListView


class ListView(BaseListView):

    def dispatch_request(self, **kwargs):
        stmt = self.get_query(**kwargs)
        pagination = stmt.paginate(*self.get_paginate_args(), error_out=self.error_out)
        context = self.get_context()
        items = self.merge_data(pagination.items)
        context.update({
            'items': items,
            'pagination': pagination
        })
        return self.render(**context)

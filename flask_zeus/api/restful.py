# encoding:utf-8
from __future__ import unicode_literals
from __future__ import absolute_import
from flask import request
from flask_restful import (Resource, marshal)
from flask_login import (login_required, current_user)
from .base import BaseResource
from .error import *


class RestfulResource(BaseResource, Resource):
    """
    example:
        from app.models import Post
        from app.forms import PostCreateForm, PostUpdateForm
        from app.output_fields import post_fields

        @api.resource('/posts/', '/posts/<int:id>/')
        class PostAPI(ModelResource):
            model = Post
            create_form = PostCreateForm
            update_form = PostUpdateForm
            output_fields = post_fields
            allow_create = True
            allow_update = True
            allow_delete = True
    """

    def get(self, **kwargs):
        """ 资源获取
        :param kwargs:
        :return: dict
        """
        self.check_model()
        self.check_output_fields()

        stmt = self.generate_stmt(**kwargs)

        if kwargs.get('id'):
            item = stmt.first()
            if not item:
                raise ZeusNotFound
            return marshal(item, self.output_fields)

        if self.allow_paginate:
            page = request.args.get('page', self.default_page, int) or self.default_page
            per_page = request.args.get('per_page', self.default_per_page, int) or self.default_per_page
            pagination = stmt.paginate(page, per_page, error_out=not self.allow_empty)
            items = self.merge_data(pagination.items)
            return {
                'items': marshal(items, self.output_fields),
                'pagination': OrderedDict([
                    ('has_prev', pagination.has_next),
                    ('has_next', pagination.has_next),
                    ('prev_num', pagination.prev_num),
                    ('next_num', pagination.next_num),
                    ('prev_url', self.generate_url(pagination.prev_num, per_page, **kwargs) if pagination.has_prev else ''),
                    ('next_url', self.generate_url(pagination.next_num, per_page, **kwargs) if pagination.has_next else ''),
                    ('page', pagination.page),
                    ('per_page', per_page),
                    ('pages', pagination.pages),
                    ('total', pagination.total),
                    ('iter_pages', self.generate_iter_pages(pagination.iter_pages(), per_page, **kwargs)),
                ])
            }
        else:
            items = stmt.all()

            if not self.allow_empty and not items:
                raise ZeusNotFound

            return marshal(items, self.output_fields)

    @login_required
    def post(self, **kwargs):
        """ 资源创建
        :param kwargs:
        :return: dict
        """
        self.check_model()
        self.check_create_form()
        self.check_output_fields()

        if not self.allow_create or not self.model.has_property('user_id'):
            raise ZeusMethodNotAllowed

        form = self.create_form(csrf_enabled=self.csrf_enabled)

        if form.validate_on_submit():
            item = self.model()
            item = item.update(commit=False, **form.data)
            item = item.update(commit=False, **kwargs)

            if self.model.has_property('user_id'):
                item.user_id = current_user.id

            item.save()
            return marshal(item, self.output_fields), 201

        raise ZeusBadRequest(details=form.errors)

    @login_required
    def put(self, **kwargs):
        """ 资源更新
        :param kwargs:
        :return: dict
        """
        self.check_model()
        self.check_update_form()
        self.check_output_fields()

        if not kwargs or not self.allow_update or not self.model.has_property('user_id'):
            raise ZeusMethodNotAllowed

        stmt = self.generate_stmt(**kwargs)
        item = stmt.first()

        if not item:
            raise ZeusNotFound

        if item.user_id != current_user.id:
            raise ZeusUnauthorized

        form = self.update_form(csrf_enabled=self.csrf_enabled)

        if form.validate_on_submit():
            item = item.update(**form.data)
            return marshal(item, self.output_fields), 200

        raise ZeusBadRequest(details=form.errors)

    @login_required
    def delete(self, **kwargs):
        """ 资源删除
        :param kwargs:
        :return: None
        """
        self.check_model()

        if not kwargs or not self.allow_delete or not self.model.has_property('user_id'):
            raise ZeusMethodNotAllowed

        if self.delete_form:
            form = self.delete_form()
            if not form.validate_on_submit():
                raise ZeusBadRequest(details=form.errors)

        stmt = self.generate_stmt(**kwargs)
        item = stmt.first()

        if not item:
            raise ZeusNotFound

        if item.user_id != current_user.id:
            raise ZeusUnauthorized

        item.delete()

        return {}, 204


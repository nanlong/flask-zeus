# encoding:utf-8
from __future__ import unicode_literals
from __future__ import absolute_import
from flask import request
from flask.ext.restful import Resource, marshal, abort
from .zeus_auth import multi_auth, api_current_user


class ModelResource(Resource):
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
    model = None
    create_form = None
    update_form = None
    output_fields = None
    allow_create = False
    allow_update = False
    allow_delete = False
    auth = None
    page = 1
    per_page = 20

    @property
    def cls_name(self):
        return self.__class__.__name__

    def check_model(self):
        assert self.model, 'API Class: {} model not set'.format(self.cls_name)

    def check_create_form(self):
        assert self.create_form, 'API Class: {} create_form not set'.format(self.cls_name)

    def check_update_form(self):
        assert self.update_form, 'API Class: {} update_form not set'.format(self.cls_name)

    def check_output_fields(self):
        assert self.output_fields, 'API Class: {} output_fields not set'.format(self.cls_name)

    def generate_stmt(self, **kwargs):
        """ 生成查询语句
        :param kwargs:
        :return:
        """
        stmt = self.model.query

        filter_by = {}
        for k, v in kwargs.iteritems():
            if self.model.has_property(k):
                filter_by[k] = v

        stmt = stmt.filter_by(**filter_by)
        return stmt

    def get(self, **kwargs):
        """ 资源获取
        :param kwargs:
        :return:
        """
        self.check_model()
        self.check_output_fields()

        stmt = self.generate_stmt(**kwargs)

        if kwargs.get('id'):
            item = stmt.first_or_404()
            return marshal(item, self.output_fields)

        stmt = stmt.order_by(self.model.id.desc())
        page = request.args.get('page', self.page, int)
        per_page = request.args.get('per_page', self.per_page, int)
        pagination = stmt.paginate(page, per_page, error_out=False)

        return {
            'items': marshal(pagination.items, self.output_fields),
            'pagination': {
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev,
                'page': pagination.page,
                'pages': pagination.pages,
                'total': pagination.total,
                'next_num': pagination.next_num,
                'prev_num': pagination.prev_num,
                'iter_pages': list(pagination.iter_pages())
            }
        }

    @multi_auth.login_required
    def post(self, **kwargs):
        """ 资源创建
        :param kwargs:
        :return:
        """
        self.check_model()
        self.check_create_form()
        self.check_output_fields()

        if kwargs or not self.allow_create or not self.model.has_property('user_id'):
            abort(405)

        form = self.create_form(csrf_enabled=False)

        if form.validate_on_submit():
            item = self.model(**form.data)
            item.user_id = api_current_user.id
            item.save()
            return marshal(item, self.output_fields), 201

        return form.errors, 400

    @multi_auth.login_required
    def put(self, **kwargs):
        """ 资源更新
        :param kwargs:
        :return:
        """
        self.check_model()
        self.check_update_form()
        self.check_output_fields()

        if not kwargs or not self.allow_update or not self.model.has_property('user_id'):
            abort(405)

        stmt = self.generate_stmt(**kwargs)
        item = stmt.first_or_404()

        if item.user_id != api_current_user.id:
            abort(401)

        form = self.update_form(csrf_enabled=False)

        if form.validate_on_submit():
            item.update(**form.data)
            return marshal(item, self.output_fields), 200

        return form.errors, 400

    @multi_auth.login_required
    def delete(self, **kwargs):
        """ 资源删除
        :param kwargs:
        :return:
        """
        self.check_model()

        if not kwargs or not self.allow_delete or not self.model.has_property('user_id'):
            return abort(405)

        stmt = self.generate_stmt(**kwargs)
        item = stmt.first_or_404()

        if item.user_id != api_current_user.id:
            abort(401)

        if self.model.has_property('deleted'):
            item.update(deleted=True)
        else:
            item.delete()

        return {}, 204

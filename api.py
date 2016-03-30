# encoding:utf-8
from __future__ import unicode_literals
from __future__ import absolute_import
from flask import request, url_for
from flask_restful import Resource, marshal, abort
from .auth import multi_auth, api_current_user
from .error import ZeusBadRequest, ZeusUnauthorized, ZeusNotFound, ZeusMethodNotAllowed


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
    # 模型
    model = None

    # 创建数据使用的表单
    create_form = None

    # 更新数据使用的表单
    update_form = None

    # 输出格式定义
    output_fields = None

    # 是否允许创建
    allow_create = False

    # 是否允许更新
    allow_update = False

    # 是否允许删除
    allow_delete = False

    # 页码
    page = 1

    # 每页数据个数
    per_page = 20

    # 是否生成包含域名的完整url
    is_full_url = False

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

    def generate_iter_pages(self, pages, per_page):
        """ 生成分页
        :param pages:
        :param per_page:
        :return:
        """
        pages = list(pages)
        iter_pages = []

        for page in pages:
            if isinstance(page, int):
                iter_pages.append({
                    'page': page,
                    'url': self.generate_url(page, per_page)
                })
            else:
                iter_pages.append({
                    'page': '...',
                    'url': ''
                })

        return iter_pages

    def generate_url(self, page, per_page):
        """ 生成链接
        :param page:
        :param per_page:
        :return:
        """
        return url_for(request.endpoint, page=page, per_page=per_page, _external=self.is_full_url)

    def get(self, **kwargs):
        """ 资源获取
        :param kwargs:
        :return:
        """
        self.check_model()
        self.check_output_fields()

        stmt = self.generate_stmt(**kwargs)

        if kwargs.get('id'):
            item = stmt.first()
            if not item:
                raise ZeusNotFound
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
                'next_url': self.generate_url(pagination.next_num, per_page) if pagination.has_next else '',
                'prev_url': self.generate_url(pagination.prev_num, per_page) if pagination.has_prev else '',
                'iter_pages': self.generate_iter_pages(pagination.iter_pages(), per_page)
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
            raise ZeusMethodNotAllowed

        form = self.create_form(csrf_enabled=False)

        if form.validate_on_submit():
            item = self.model(**form.data)
            item.user_id = api_current_user.id
            item.save()
            return marshal(item, self.output_fields), 201

        raise ZeusBadRequest(details=form.errors)

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
            raise ZeusMethodNotAllowed

        stmt = self.generate_stmt(**kwargs)
        item = stmt.first()

        if not item:
            raise ZeusNotFound

        if item.user_id != api_current_user.id:
            raise ZeusUnauthorized

        form = self.update_form(csrf_enabled=False)

        if form.validate_on_submit():
            item.update(**form.data)
            return marshal(item, self.output_fields), 200

        raise ZeusBadRequest(details=form.errors)

    @multi_auth.login_required
    def delete(self, **kwargs):
        """ 资源删除
        :param kwargs:
        :return:
        """
        self.check_model()

        if not kwargs or not self.allow_delete or not self.model.has_property('user_id'):
            raise ZeusMethodNotAllowed

        stmt = self.generate_stmt(**kwargs)
        item = stmt.first()

        if not item:
            raise ZeusNotFound

        if item.user_id != api_current_user.id:
            raise ZeusUnauthorized

        if self.model.has_property('deleted'):
            item.update(deleted=True)
        else:
            item.delete()

        return {}, 204

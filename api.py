# encoding:utf-8
from __future__ import unicode_literals
from __future__ import absolute_import
from flask import request, url_for
from flask_restful import Resource, marshal
from collections import OrderedDict
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
    # type: sqlalchemy obj 需要继承 CRUDMixin
    model = None

    # 创建数据使用的表单
    # type: wtforms obj
    create_form = None

    # 更新数据使用的表单
    # type: wtforms obj
    update_form = None

    # 输出格式定义
    # type: flask_restful fields obj
    output_fields = None

    # 是否允许创建
    # type: bool
    allow_create = False

    # 是否允许更新
    # type: bool
    allow_update = False

    # 是否允许删除
    # type: bool
    allow_delete = False

    # 页码
    # type: int
    page = 1

    # 每页数据个数
    # type: int
    per_page = 20

    # 是否生成包含域名的完整url
    # type: bool
    is_full_url = False

    # 自定义排序
    # type: list or tuple or set
    order_by = None

    @property
    def cls_name(self):
        """ 视图类名称
        :return: str
        """
        return self.__class__.__name__

    def check_model(self):
        """ 检查模型是否设置
        :return:
        """
        assert self.model, 'API Class: {} model not set'.format(self.cls_name)

    def check_create_form(self):
        """ 检查创建表单是否设置
        :return:
        """
        assert self.create_form, 'API Class: {} create_form not set'.format(self.cls_name)

    def check_update_form(self):
        """ 检查更新表单是否设置
        :return:
        """
        assert self.update_form, 'API Class: {} update_form not set'.format(self.cls_name)

    def check_output_fields(self):
        """ 检查输出格式是否设置
        :return:
        """
        assert self.output_fields, 'API Class: {} output_fields not set'.format(self.cls_name)

    @property
    def stmt(self):
        """ 自定义stmt语句, 需重写, 提供给get方法使用
        :return: sqlalchemy query
        """
        return None

    def generate_stmt(self, **kwargs):
        """ 生成查询语句
        :param kwargs:
        :return: sqlalchemy query
        """
        if self.stmt:
            return self.stmt

        stmt = self.model.query

        filter_by = {}
        for k, v in kwargs.iteritems():
            if self.model.has_property(k):
                filter_by[k] = v

        stmt = stmt.filter_by(**filter_by)

        if self.order_by and isinstance(self.order_by, (list, tuple, set)):
            stmt = stmt.order_by(*self.order_by)

        return stmt

    def generate_iter_pages(self, pages, per_page):
        """ 生成分页
        :param pages:
        :param per_page:
        :return: list
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
        :return: str
        """
        return url_for(request.endpoint, page=page, per_page=per_page, _external=self.is_full_url)

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

        page = request.args.get('page', self.page, int)
        per_page = request.args.get('per_page', self.per_page, int)
        pagination = stmt.paginate(page, per_page, error_out=False)

        return {
            'items': marshal(pagination.items, self.output_fields),
            'pagination': OrderedDict([
                ('has_prev', pagination.has_next),
                ('has_next', pagination.has_next),
                ('prev_num', pagination.prev_num),
                ('next_num', pagination.next_num),
                ('prev_url', self.generate_url(pagination.prev_num, per_page) if pagination.has_prev else ''),
                ('next_url', self.generate_url(pagination.next_num, per_page) if pagination.has_next else ''),
                ('page', pagination.page),
                ('pages', pagination.pages),
                ('total', pagination.total),
                ('iter_pages', self.generate_iter_pages(pagination.iter_pages(), per_page)),
            ])
        }

    @multi_auth.login_required
    def post(self, **kwargs):
        """ 资源创建
        :param kwargs:
        :return: dict
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
        :return: None
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

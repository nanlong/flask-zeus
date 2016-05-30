# encoding:utf-8
from __future__ import unicode_literals
from __future__ import absolute_import
from flask import (request, url_for)


class BaseResource(object):
    # 模型
    # type: sqlalchemy obj 需要继承 CRUDMixin
    model = None

    # 创建数据使用的表单
    # type: wtforms obj
    create_form = None

    # 更新数据使用的表单
    # type: wtforms obj
    update_form = None

    # 删除数据使用的表单
    # type: wtforms obj
    delete_form = None

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

    # 是否允许返回空数据
    # type: bool
    allow_empty = True

    # 是否显示分页
    # type: bool
    allow_paginate = True

    # 页码
    # type: int
    default_page = 1

    # 每页数据个数
    # type: int
    default_per_page = 20

    # 是否生成包含域名的完整url
    # type: bool
    is_full_url = True

    # 自定义排序
    # type: list or tuple or set
    order_by = None

    # 是否开始csrf验证
    # type: bool
    csrf_enabled = True

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

    def get_stmt(self, **kwargs):
        """ 自定义stmt语句, 需重写, 提供给get方法使用
        :return: sqlalchemy query
        """
        return None

    def generate_stmt(self, **kwargs):
        """ 生成查询语句
        :param kwargs:
        :return: sqlalchemy query
        """
        # 如有自定义语句,直接返回
        if self.get_stmt(**kwargs):
            return self.get_stmt(**kwargs)

        stmt = self.model.query

        # 处理url主体,?之前
        filter_by_ = {}

        for k, v in kwargs.items():
            if self.model.has_property(k):
                filter_by_[k] = v

        if filter_by_:
            stmt = stmt.filter_by(**filter_by_)

        # 处理url参数?之后
        # 默认参数为多值,使用in操作符
        # 如果参数为单值,并且开头或结尾为%,使用like操作符
        filter_ = []

        for k, v in request.args.lists():
            if self.model.has_property(k):
                if len(v) == 1 and (v[0].startswith('%') or v[0].endswith('%')):
                    filter_.append(getattr(self.model, k).ilike(v[0]))
                else:
                    filter_.append(getattr(self.model, k).in_(v))

        if filter_:
            stmt = stmt.filter(*filter_)

        # 处理自定义排序
        if self.order_by and isinstance(self.order_by, (list, tuple)):
            stmt = stmt.order_by(*self.order_by)

        if self.model.has_property('deleted'):
            stmt = stmt.filter_by(deleted=False)

        return stmt

    def generate_iter_pages(self, pages, per_page, **kwargs):
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
                    'url': self.generate_url(page, per_page, **kwargs)
                })
            else:
                iter_pages.append({
                    'page': '...',
                    'url': ''
                })

        return iter_pages

    def generate_url(self, page, per_page, **kwargs):
        """ 生成链接
        :param page:
        :param per_page:
        :return: str
        """
        return url_for(request.endpoint, page=page, per_page=per_page, _external=self.is_full_url, **kwargs)

    def merge_data(self, data):
        return data
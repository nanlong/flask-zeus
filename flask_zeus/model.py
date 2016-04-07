# encoding:utf-8
"""
1. 尽量避免使用外键关联
2. 定义字段的时候请完善doc参数
    id = db.Column('id', db.INT, primary_key=True, doc='主键ID')
"""
from __future__ import unicode_literals
from __future__ import absolute_import
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import text
from datetime import datetime

db = SQLAlchemy()


class BaseMixin(object):
    """ Base mixin
    """
    __table_args__ = {'extend_existing': True}

    @classmethod
    def column_properties(cls):
        properties = []
        mapper = getattr(cls, '__mapper__')

        if mapper and hasattr(mapper, 'iterate_properties'):
            properties = [p.key for p in mapper.iterate_properties if isinstance(p, orm.ColumnProperty)]

        return properties

    def as_dict(self, include=None, exclude=None):
        """
        :param include: 需要显示的属性列表
        :param exclude: 需要排除的属性列表
        :return:
        """
        fields = [field.strip('_') for field in self.column_properties()]

        exportable_fields = (include or []) + fields
        exportable_fields = set(exportable_fields) - set(exclude or [])

        result = dict()
        for field in exportable_fields:
            value = getattr(self, field)
            if hasattr(value, '__call__'):
                value = value()
            result[field] = value

        return result

    @classmethod
    def has_property(cls, name):
        return name in cls.column_properties()


class CRUDMixin(BaseMixin):
    """ Basic CRUD mixin
    """
    __mapper_args__ = {
        'order_by': text('id desc')
    }

    @declared_attr
    def id(self):
        return db.Column('id', db.INT, primary_key=True, doc='主键ID')

    @declared_attr
    def created_at(self):
        return db.Column('created_at', db.TIMESTAMP, default=datetime.now, index=True, nullable=False, doc='创建时间')

    @declared_attr
    def updated_at(self):
        return db.Column('updated_at', db.TIMESTAMP, default=datetime.now, index=True, nullable=False, doc='更新时间')

    @classmethod
    def get(cls, row_id):
        return cls.query.get(row_id)

    @classmethod
    def create(cls, commit=True, **kwargs):
        return cls(**kwargs).save(commit)

    def update(self, commit=True, **kwargs):
        return self._set_attributes(**kwargs).save(commit)

    def save(self, commit=True):
        db.session.add(self)

        if commit:
            db.session.commit()

        return self

    def delete(self, commit=True):
        if self.has_property('deleted'):
            setattr(self, 'deleted', True)
            db.session.add(self)
        else:
            db.session.delete(self)

        if commit:
            db.session.commit()

    def _set_attributes(self, **kwargs):
        for k, v in kwargs.iteritems():

            if k.startswith('_'):
                raise ValueError('私有属性不允许被设置')

            if self.has_property(k):
                setattr(self, k, v)

        return self


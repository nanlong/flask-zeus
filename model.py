# encoding:utf-8
from __future__ import unicode_literals
from __future__ import absolute_import
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import orm
import datetime

db = SQLAlchemy()


class BaseMixin(object):
    """ Base mixin
    """
    __table_args__ = {'extend_existing': True}

    @classmethod
    def column_properties(cls):
        return [p.key for p in cls.__mapper__.iterate_properties
                if isinstance(p, orm.ColumnProperty)]

    def as_dict(self, include=None, exclude=None):
        """ method for building dictionary for model value-properties filled
            with data from mapped storage backend
        :param include:
        :param exclude:
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

    id = db.Column('id', db.INT, primary_key=True)
    created_at = db.Column('created_at', db.TIMESTAMP, default=datetime.datetime.now, index=True, nullable=False)
    updated_at = db.Column('updated_at', db.TIMESTAMP, default=datetime.datetime.now, index=True, nullable=False)

    __mapper_args__ = {
        'order_by': id.desc()
    }

    @classmethod
    def get(cls, row_id):
        return cls.query.get(row_id)

    @classmethod
    def create(cls, commit=True, **kwargs):
        return cls(**kwargs).save(commit)

    def update(self, commit=True, **kwargs):
        return self._setattrs(**kwargs).save(commit)

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        db.session.delete(self)
        if commit:
            db.session.commit()

    def _setattrs(self, **kwargs):
        for k, v in kwargs.iteritems():
            if k.startswith('_'):
                raise ValueError('Underscored values are not allowed')
            setattr(self, k, v)
        return self


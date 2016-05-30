# encoding:utf-8
from __future__ import unicode_literals
from __future__ import absolute_import
from flask import (redirect, flash)
from flask_login import (current_user)
from .base import BaseFormView


class CreateView(BaseFormView):

    def dispatch_request(self, **kwargs):
        form = self.get_form()(csrf_enabled=self.csrf_enabled)

        if form.validate_on_submit():

            item = self.model()

            for k, v in form.data.iteritems():
                setattr(item, k, v)

            item = item.update(commit=False, **kwargs)

            if self.model.has_property('user_id'):
                item.user_id = current_user.id

            item.save()

            if self.success_message:
                flash(self.success_message, category='success')

            return redirect(self.get_next_url(**kwargs))

        context = self.get_context()
        context.update({
            'form': form
        })
        return self.render(**context)


class UpdateView(BaseFormView):

    def dispatch_request(self, **kwargs):

        stmt = self.get_query(**kwargs)
        item = stmt.first_or_404()

        form = self.get_form()(obj=item, csrf_enabled=self.csrf_enabled)

        if form.validate_on_submit():

            for k, v in form.data.iteritems():
                setattr(item, k, v)

            item = item.update(commit=False, **kwargs)

            if self.model.has_property('user_id'):
                item.user_id = current_user.id

            item.save()

            if self.success_message:
                flash(self.success_message, category='success')

            return redirect(self.get_next_url(**kwargs))

        context = self.get_context()
        context.update({
            'form': form
        })
        return self.render(**context)

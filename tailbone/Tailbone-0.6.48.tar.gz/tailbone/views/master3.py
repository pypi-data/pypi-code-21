# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Master View
"""

from __future__ import unicode_literals, absolute_import

import os

from sqlalchemy import orm

import deform
from webhelpers2.html import tags

from tailbone import forms2 as forms
from tailbone.views import MasterView2


class MasterView3(MasterView2):
    """
    Base "master" view class.  All model master views should derive from this.
    """

    @classmethod
    def get_form_factory(cls):
        """
        Returns the grid factory or class which is to be used when creating new
        grid instances.
        """
        return getattr(cls, 'form_factory', forms.Form)

    def make_form(self, instance=None, factory=None, fields=None, schema=None, **kwargs):
        """
        Creates a new form for the given model class/instance
        """
        if factory is None:
            factory = self.get_form_factory()
        if fields is None:
            fields = self.get_form_fields()
        if schema is None:
            schema = self.make_form_schema()

        if not self.creating:
            kwargs['model_instance'] = instance
        kwargs = self.make_form_kwargs(**kwargs)
        form = factory(fields, schema, **kwargs)
        self.configure_form(form)
        return form

    def make_form_schema(self):
        if not self.model_class:
            # TODO
            raise NotImplementedError

    def get_form_fields(self):
        if hasattr(self, 'form_fields'):
            return self.form_fields
        # TODO
        # raise NotImplementedError

    def make_form_kwargs(self, **kwargs):
        """
        Return a dictionary of kwargs to be passed to the factory when creating
        new form instances.
        """
        defaults = {
            'request': self.request,
            'readonly': self.viewing,
            'model_class': getattr(self, 'model_class', None),
            'action_url': self.request.current_route_url(_query=None),
        }
        if self.creating:
            kwargs.setdefault('cancel_url', self.get_index_url())
        else:
            instance = kwargs['model_instance']
            kwargs.setdefault('cancel_url', self.get_action_url('view', instance))
        defaults.update(kwargs)
        return defaults

    def configure_form(self, form):
        """
        Configure the primary form.  By default this just sets any primary key
        fields to be readonly (if we have a :attr:`model_class`).
        """

        if self.editing and self.model_class:
            mapper = orm.class_mapper(self.model_class)
            for key in mapper.primary_key:
                for field in form.fields:
                    if field == key.name:
                        form.set_readonly(field)
                        break

        form.remove_field('uuid')

        self.set_labels(form)

    def render_file_field(self, path, url=None, filename=None):
        """
        Convenience for rendering a file with optional download link
        """
        if not filename:
            filename = os.path.basename(path)
        content = "{} ({})".format(filename, self.readable_size(path))
        if url:
            return tags.link_to(content, url)
        return content

    def readable_size(self, path):
        # TODO: this was shamelessly copied from FormAlchemy ...
        length = self.get_size(path)
        if length == 0:
            return '0 KB'
        if length <= 1024:
            return '1 KB'
        if length > 1048576:
            return '%0.02f MB' % (length / 1048576.0)
        return '%0.02f KB' % (length / 1024.0)

    def get_size(self, path):
        try:
            return os.path.getsize(path)
        except os.error:
            return 0

    def validate_form(self, form):
        controls = self.request.POST.items()
        try:
            self.form_deserialized = form.validate(controls)
        except deform.ValidationFailure:
            return False
        return True

    def save_create_form(self, form):
        self.before_create(form)
        obj = form.schema.objectify(self.form_deserialized)
        self.before_create_flush(obj, form)
        self.Session.add(obj)
        self.Session.flush()
        return obj

    def before_create_flush(self, obj, form):
        pass

    def save_edit_form(self, form):
        obj = form.schema.objectify(self.form_deserialized, context=form.model_instance)
        self.after_edit(obj)
        self.Session.flush()

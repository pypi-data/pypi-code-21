# -*- coding: utf-8 -*-
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
Forms Core
"""

from __future__ import unicode_literals, absolute_import

from rattail.util import OrderedDict, prettify

import formalchemy
from formalchemy.helpers import content_tag
from pyramid.renderers import render


class Form(object):
    """
    Base class for all forms.
    """
    create_label = "Create"
    update_label = "Save"

    def __init__(self, request, readonly=False, action_url=None):
        self.request = request
        self.readonly = readonly
        self.action_url = action_url

    def render(self, **kwargs):
        kwargs.setdefault('form', self)
        if self.readonly:
            template = '/forms/form_readonly.mako'
        else:
            template = '/forms/form.mako'
        return render(template, kwargs)

    def render_fields(self, **kwargs):
        kwargs.setdefault('fieldset', self.fieldset)
        if self.readonly:
            template = '/forms/fieldset_readonly.mako'
        else:
            template = '/forms/fieldset.mako'
        return render(template, kwargs)


class Field(object):
    """
    Manually create instances of this class to populate a simple form.
    """

    def __init__(self, name, value=None, label=None, requires_label=True):
        self.name = name
        self.value = value
        self._label = label or prettify(self.name)
        self.requires_label = requires_label

    def is_required(self):
        return True

    def label(self):
        return self._label

    def label_tag(self, **html_options):
        """
        Logic stolen from FormAlchemy so all fields can render their own label.
        Original docstring follows.

        return the <label /> tag for the field.
        """
        html_options.update(for_=self.name)
        if 'class_' in html_options:
            html_options['class_'] += self.is_required() and ' field_req' or ' field_opt'
        else:
            html_options['class_'] = self.is_required() and 'field_req' or 'field_opt'
        return content_tag('label', self.label(), **html_options)

    def render_readonly(self):
        if self.value is None:
            return ''
        return unicode(self.value)


class FieldSet(object):
    """
    Generic fieldset for use with manually-created simple forms.
    """

    def __init__(self):
        self.fields = OrderedDict()
        self.render_fields = self.fields


class GenericFieldSet(formalchemy.FieldSet):
    """
    FieldSet class based on FormAlchemy, but without the SQLAlchemy magic.
    """
    __sa__ = False
    _bound_pk = None
    data = None
    prettify = staticmethod(prettify)

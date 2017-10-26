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
Simple Forms
"""

from __future__ import unicode_literals, absolute_import

from rattail.util import prettify

import pyramid_simpleform
from pyramid_simpleform import renderers
from webhelpers2.html import tags, HTML

from tailbone.forms import Form


class SimpleForm(Form):
    """
    Customized simple form.
    """

    def __init__(self, request, schema, obj=None, **kwargs):
        super(SimpleForm, self).__init__(request, **kwargs)
        self._form = pyramid_simpleform.Form(request, schema=schema, obj=obj)

    def __getattr__(self, attr):
        return getattr(self._form, attr)

    def render(self, **kwargs):
        kwargs['form'] = FormRenderer(self)
        return super(SimpleForm, self).render(**kwargs)

    def validate(self):
        return self._form.validate()


class FormRenderer(renderers.FormRenderer):
    """
    Customized form renderer.  Provides some extra methods for convenience.
    """

    def __getattr__(self, attr):
        return getattr(self.form, attr)

    def field_div(self, name, field, label=None):
        errors = self.errors_for(name)
        if errors:
            errors = [HTML.tag('div', class_='field-error', c=x) for x in errors]
            errors = tags.literal('').join(errors)

        label = HTML.tag('label', for_=name, c=label or prettify(name))
        inner = HTML.tag('div', class_='field', c=field)

        outer_class = 'field-wrapper'
        if errors:
            outer_class += ' error'
        outer = HTML.tag('div', class_=outer_class, c=(errors or '') + label + inner)
        return outer

    def referrer_field(self):
        return self.hidden('referrer', value=self.form.request.get_referrer())

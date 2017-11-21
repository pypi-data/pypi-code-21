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
Core Field Renderers
"""

from __future__ import unicode_literals, absolute_import

import datetime

import formalchemy as fa
from formalchemy.fields import AbstractField
from pyramid.renderers import render


class CustomFieldRenderer(fa.FieldRenderer):
    """
    Base class for renderers which accept customization args, and "fake out"
    FormAlchemy by pretending to still be a renderer factory when in fact it's
    already dealing with a renderer instance.
    """

    def __init__(self, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], AbstractField):
            super(CustomFieldRenderer, self).__init__(args[0])
            self.init(**kwargs)
        else:
            assert len(args) == 0
            self.init(**kwargs)

    def __call__(self, field):
        super(CustomFieldRenderer, self).__init__(field)
        return self

    def init(self, **kwargs):
        pass

    @property
    def rattail_config(self):
        return self.request.rattail_config


class DateFieldRenderer(CustomFieldRenderer, fa.DateFieldRenderer):
    """
    Date field renderer which uses jQuery UI datepicker widget when rendering
    in edit mode.
    """
    date_format = '%Y-%m-%d'
    change_year = False

    def init(self, date_format=None, change_year=False):
        if date_format:
            self.date_format = date_format
        self.change_year = change_year

    def render_readonly(self, **kwargs):
        value = self.raw_value
        if value is None:
            return ''
        return value.strftime(self.date_format)

    def render(self, **kwargs):
        kwargs['name'] = self.name
        kwargs['value'] = self.value
        kwargs['change_year'] = self.change_year
        return render('/forms/fields/date.mako', kwargs)

    def deserialize(self):
        value = self._serialized_value()
        if not value:
            return None
        try:
            return datetime.datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            raise fa.ValidationError("Date value must be in YYYY-MM-DD format")
        except Exception as error:
            raise fa.ValidationError(unicode(error))

    def _serialized_value(self):
        return self.params.getone(self.name)

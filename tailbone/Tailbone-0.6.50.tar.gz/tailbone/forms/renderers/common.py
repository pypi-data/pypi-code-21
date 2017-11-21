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
Common Field Renderers
"""

from __future__ import unicode_literals, absolute_import

import datetime

from rattail.time import localtime, make_utc
from rattail.util import pretty_quantity

import formalchemy as fa
from formalchemy import fields as fa_fields, helpers as fa_helpers
from pyramid.renderers import render
from webhelpers2.html import HTML, tags

from tailbone.util import pretty_datetime, raw_datetime


class StrippedTextFieldRenderer(fa.TextFieldRenderer):
    """
    Standard text field renderer, which strips whitespace from either end of
    the input value on deserialization.
    """

    def deserialize(self):
        value = super(StrippedTextFieldRenderer, self).deserialize()
        if value is not None:
            return value.strip()


class CodeTextAreaFieldRenderer(fa.TextAreaFieldRenderer):

    def render_readonly(self, **kwargs):
        value = self.raw_value
        if not value:
            return ''
        return HTML.tag('pre', c=value)

    def render(self, **kwargs):
        kwargs.setdefault('size', (80, 8))
        return super(CodeTextAreaFieldRenderer, self).render(**kwargs)


class AutocompleteFieldRenderer(fa.FieldRenderer):
    """
    Custom renderer for an autocomplete field.
    """

    service_route = None
    width = '300px'

    @property
    def focus_name(self):
        return self.name + '-textbox'

    @property
    def needs_focus(self):
        return not bool(self.value or self.field_value)

    @property
    def field_display(self):
        return self.raw_value

    @property
    def field_value(self):
        return self.value

    @property
    def service_url(self):
        return self.request.route_url(self.service_route)

    def render(self, options=None, **kwargs):
        if kwargs.pop('autocomplete', True):
            return self.render_autocomplete(**kwargs)
        # 'selected' is a kwarg for autocomplete template *and* select tag
        kwargs.pop('selected', None)
        return self.render_dropdown(options, **kwargs)

    def render_autocomplete(self, **kwargs):
        kwargs.setdefault('field_name', self.name)
        kwargs.setdefault('field_value', self.field_value)
        kwargs.setdefault('field_display', self.field_display)
        kwargs.setdefault('service_url', self.service_url)
        kwargs.setdefault('width', self.width)
        return render('/forms/field_autocomplete.mako', kwargs)

    def render_dropdown(self, options, **kwargs):
        # NOTE: this logic copied from formalchemy.fields.SelectFieldRenderer.render()
        kwargs.setdefault('auto-enhance', 'true')
        if callable(options):
            L = fa_fields._normalized_options(options(self.field.parent))
            if not self.field.is_required() and not self.field.is_collection:
                L.insert(0, self.field._null_option)
        else:
            L = list(options)
        if len(L) > 0:
            if len(L[0]) == 2:
                L = [(k, self.stringify_value(v)) for k, v in L]
            else:
                L = [fa_fields._stringify(k) for k in L]
        return fa_fields.h.select(self.name, self.value, L, **kwargs)

    def render_readonly(self, **kwargs):
        value = self.field_display
        if value is None:
            return u''
        return unicode(value)


class DateTimeFieldRenderer(fa.DateTimeFieldRenderer):
    """
    This renderer assumes the datetime field value is in UTC, and will convert
    it to the local time zone before rendering it in the standard "raw" format.
    """

    def render_readonly(self, **kwargs):
        value = self.raw_value
        if not value:
            return ''
        return raw_datetime(self.request.rattail_config, value)


class DateTimePrettyFieldRenderer(fa.DateTimeFieldRenderer):
    """
    Custom date/time field renderer, which displays a "pretty" value in
    read-only mode, leveraging config to show the correct timezone.
    """

    def render_readonly(self, **kwargs):
        value = self.raw_value
        if not value:
            return ''
        return pretty_datetime(self.request.rattail_config, value)


class LocalDateTimeFieldRenderer(fa.DateTimeFieldRenderer):
    """
    This renderer assumes the datetime field value is "naive" in local time zone.
    """

    def render_readonly(self, **kwargs):
        value = self.raw_value
        if not value:
            return ''
        value = localtime(self.request.rattail_config, value)
        return raw_datetime(self.request.rattail_config, value)


class TimeFieldRenderer(fa.TimeFieldRenderer):
    """
    Custom renderer for time fields.  In edit mode, renders a simple text
    input, which is expected to become a 'timepicker' widget in the UI.
    However the particular magic required for that lives in 'tailbone.js'.
    """
    format = '%I:%M %p'

    def render(self, **kwargs):
        kwargs.setdefault('class_', 'timepicker')
        return fa_helpers.text_field(self.name, value=self.value, **kwargs)

    def render_readonly(self, **kwargs):
        return self.render_value(self.raw_value)

    def render_value(self, value):
        value = self.convert_value(value)
        if isinstance(value, datetime.time):
            return value.strftime(self.format)
        return ''

    def convert_value(self, value):
        if isinstance(value, datetime.datetime):
            if not value.tzinfo:
                value = make_utc(value, tzinfo=True)
            return localtime(self.request.rattail_config, value).time()
        return value

    def stringify_value(self, value, as_html=False):
        if not as_html:
            return self.render_value(value)
        return super(TimeFieldRenderer, self).stringify_value(value, as_html=as_html)

    def _serialized_value(self):
        return self.params.getone(self.name)

    def deserialize(self):
        value = self._serialized_value()
        if value:
            try:
                return datetime.datetime.strptime(value, self.format).time()
            except ValueError:
                pass


class EmailFieldRenderer(fa.TextFieldRenderer):
    """
    Renderer for email address fields
    """

    def render_readonly(self, **kwargs):
        address = self.raw_value
        if not address:
            return ''
        return tags.link_to(address, 'mailto:{}'.format(address))


class EnumFieldRenderer(fa_fields.SelectFieldRenderer):
    """
    Renderer for simple enumeration fields.
    """
    enumeration = {}
    render_key = False

    def __init__(self, arg, render_key=False):
        if isinstance(arg, dict):
            self.enumeration = arg
            self.render_key = render_key
        else:
            self(arg)

    def __call__(self, field):
        super(EnumFieldRenderer, self).__init__(field)
        return self

    def render_readonly(self, **kwargs):
        value = self.raw_value
        if value is None:
            return ''
        rendered = self.enumeration.get(value, unicode(value))
        if self.render_key:
            rendered = '{} - {}'.format(value, rendered)
        return rendered

    def render(self, **kwargs):
        opts = [(self.enumeration[x], x) for x in self.enumeration]
        if not self.field.is_required():
            opts.insert(0, self.field._null_option)
        return fa_fields.SelectFieldRenderer.render(self, opts, **kwargs)


class DecimalFieldRenderer(fa.FieldRenderer):
    """
    Sort of generic field renderer for decimal values.  You must provide the
    number of places after the decimal (scale).  Note that this in turn relies
    on simple string formatting; the renderer does not attempt any mathematics
    of its own.
    """

    def __init__(self, scale):
        self.scale = scale

    def __call__(self, field):
        super(DecimalFieldRenderer, self).__init__(field)
        return self

    def render_readonly(self, **kwargs):
        value = self.raw_value
        if value is None:
            return ''
        fmt = '{{0:0.{0}f}}'.format(self.scale)
        return fmt.format(value)


class CurrencyFieldRenderer(fa_fields.FloatFieldRenderer):
    """
    Sort of generic field renderer for currency values.
    """

    def render_readonly(self, **kwargs):
        value = self.raw_value
        if value is None:
            return ''
        if value < 0:
            return "(${:0,.2f})".format(0 - value)
        return "${:0,.2f}".format(value)


class QuantityFieldRenderer(fa_fields.FloatFieldRenderer):
    """
    Sort of generic field renderer for quantity values.
    """

    def render_readonly(self, **kwargs):
        return pretty_quantity(self.raw_value)


class YesNoFieldRenderer(fa.CheckBoxFieldRenderer):

    def render_readonly(self, **kwargs):
        value = self.raw_value
        if value is None:
            return u''
        return u'Yes' if value else u'No'

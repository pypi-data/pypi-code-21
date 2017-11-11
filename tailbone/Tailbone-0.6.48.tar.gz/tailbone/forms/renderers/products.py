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
Product Field Renderers
"""

from __future__ import unicode_literals, absolute_import

import six

from rattail.gpc import GPC
from rattail.db import model
from rattail.db.util import maxlen

import formalchemy as fa
from formalchemy import TextFieldRenderer
from formalchemy.fields import SelectFieldRenderer
from webhelpers2.html import tags, literal

from tailbone.forms.renderers.common import AutocompleteFieldRenderer
from tailbone.util import pretty_datetime


class ProductFieldRenderer(AutocompleteFieldRenderer):
    """
    Renderer for :class:`rattail.db.model.Product` instance fields.
    """

    service_route = 'products.autocomplete'

    @property
    def field_display(self):
        product = self.raw_value
        if product:
            return product.full_description
        return ''

    def render_readonly(self, **kwargs):
        product = self.raw_value
        if not product:
            return ""
        render = kwargs.get('render_product', self.render_product)
        text = render(product)
        if kwargs.get('hyperlink', True):
            return tags.link_to(text, self.request.route_url('products.view', uuid=product.uuid))
        return text

    def render_product(self, product):
        return six.text_type(product)


class ProductKeyFieldRenderer(TextFieldRenderer):
    """
    Base class for product key field renderers.
    """

    def render_readonly(self, **kwargs):
        value = self.raw_value
        if value is None:
            return ''
        value = self.render_value(value)
        if kwargs.get('link'):
            product = self.field.parent.model
            value = tags.link_to(value, kwargs['link'](product))
        return value

    def render_value(self, value):
        return unicode(value)


class GPCFieldRenderer(ProductKeyFieldRenderer):
    """
    Renderer for :class:`rattail.gpc.GPC` fields.
    """

    @property
    def length(self):
        # Hm, should maybe consider hard-coding this...?
        return len(unicode(GPC(0)))

    def render_value(self, gpc):
        return gpc.pretty()


class ScancodeFieldRenderer(ProductKeyFieldRenderer):
    """
    Renderer for :class:`rattail.db.model.Product.scancode` field
    """

    @property
    def length(self):
        return maxlen(model.Product.scancode)


class DepartmentFieldRenderer(SelectFieldRenderer):
    """
    Shows the department number as well as the name.
    """

    def render(self, **kwargs):
        kwargs.setdefault('auto-enhance', 'true')
        return super(DepartmentFieldRenderer, self).render(**kwargs)

    def render_readonly(self, **kwargs):
        department = self.raw_value
        if not department:
            return ''
        if department.number:
            text = '({}) {}'.format(department.number, department.name)
        else:
            text = department.name
        return tags.link_to(text, self.request.route_url('departments.view', uuid=department.uuid))


class SubdepartmentFieldRenderer(SelectFieldRenderer):
    """
    Shows a link to the subdepartment.
    """

    def render_readonly(self, **kwargs):
        subdept = self.raw_value
        if not subdept:
            return ""
        if subdept.number:
            text = "({}) {}".format(subdept.number, subdept.name)
        else:
            text = subdept.name
        return tags.link_to(text, self.request.route_url('subdepartments.view', uuid=subdept.uuid))


class CategoryFieldRenderer(SelectFieldRenderer):
    """
    Shows a link to the category.
    """

    def render_readonly(self, **kwargs):
        category = self.raw_value
        if not category:
            return ""
        if category.code:
            text = "({}) {}".format(category.code, category.name)
        else:
            text = category.name
        return tags.link_to(text, self.request.route_url('categories.view', uuid=category.uuid))


class BrandFieldRenderer(AutocompleteFieldRenderer):
    """
    Renderer for :class:`rattail.db.model.Brand` instance fields.
    """

    service_route = 'brands.autocomplete'


class CostFieldRenderer(fa.FieldRenderer):
    """
    Renders fields which reference a ProductCost object
    """

    def render_readonly(self, **kwargs):
        cost = self.raw_value
        if not cost:
            return ''
        return '${:0.2f}'.format(cost.unit_cost)


class PriceFieldRenderer(TextFieldRenderer):
    """
    Renderer for fields which reference a :class:`ProductPrice` instance.
    """

    def render_readonly(self, **kwargs):
        price = self.field.raw_value
        if price:
            if not price.product.not_for_sale:
                if price.price is not None and price.pack_price is not None:
                    if price.multiple > 1:
                        return literal('$ %0.2f / %u&nbsp; ($ %0.2f / %u)' % (
                                price.price, price.multiple,
                                price.pack_price, price.pack_multiple))
                    return literal('$ %0.2f&nbsp; ($ %0.2f / %u)' % (
                            price.price, price.pack_price, price.pack_multiple))
                if price.price is not None:
                    if price.multiple > 1:
                        return '$ %0.2f / %u' % (price.price, price.multiple)
                    return '$ %0.2f' % price.price
                if price.pack_price is not None:
                    return '$ %0.2f / %u' % (price.pack_price, price.pack_multiple)
        return ''


class PriceWithExpirationFieldRenderer(PriceFieldRenderer):
    """
    Price field renderer which also displays the expiration date, if present.
    """

    def render_readonly(self, **kwargs):
        result = super(PriceWithExpirationFieldRenderer, self).render_readonly(**kwargs)
        if result:
            price = self.field.raw_value
            if price.ends:
                result = '{0}&nbsp; ({1})'.format(
                    result, pretty_datetime(self.request.rattail_config, price.ends))
        return result

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
Vendor Field Renderers
"""

from __future__ import unicode_literals, absolute_import

from formalchemy.fields import SelectFieldRenderer
from webhelpers2.html import tags

from tailbone.forms.renderers.common import AutocompleteFieldRenderer


class VendorFieldRenderer(AutocompleteFieldRenderer):
    """
    Renderer for :class:`rattail.db.model.Vendor` instance fields.
    """
    service_route = 'vendors.autocomplete'

    def render_readonly(self, **kwargs):
        vendor = self.raw_value
        if not vendor:
            return ""
        text = "({}) {}".format(vendor.id, vendor.name)
        if kwargs.get('hyperlink', True):
            return tags.link_to(text, self.request.route_url('vendors.view', uuid=vendor.uuid))
        return text


class PurchaseFieldRenderer(SelectFieldRenderer):
    """
    Renderer for :class:`rattail.db.model.Purchase` relation fields.
    """

    def render_readonly(self, **kwargs):
        purchase = self.raw_value
        if not purchase:
            return ''
        return tags.link_to(purchase, self.request.route_url('purchases.view', uuid=purchase.uuid))

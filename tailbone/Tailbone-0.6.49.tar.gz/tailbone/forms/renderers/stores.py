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
Store Field Renderers
"""

from __future__ import unicode_literals, absolute_import

from formalchemy.fields import SelectFieldRenderer
from webhelpers2.html import tags


class StoreFieldRenderer(SelectFieldRenderer):
    """
    Renderer for :class:`rattail.db.model.Store` instance fields.
    """

    def render(self, **kwargs):
        kwargs.setdefault('auto-enhance', 'true')
        return super(StoreFieldRenderer, self).render(**kwargs)

    def render_readonly(self, **kwargs):
        store = self.raw_value
        if not store:
            return ""
        text = "({}) {}".format(store.id, store.name)
        if kwargs.get('hyperlink', True):
            return tags.link_to(text, self.request.route_url('stores.view', uuid=store.uuid))
        return text

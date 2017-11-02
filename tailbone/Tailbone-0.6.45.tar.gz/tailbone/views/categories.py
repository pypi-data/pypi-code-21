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
Category Views
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model

from tailbone.views import MasterView3 as MasterView


class CategoriesView(MasterView):
    """
    Master view for the Category class.
    """
    model_class = model.Category
    model_title_plural = "Categories"
    route_prefix = 'categories'
    has_versions = True

    grid_columns = [
        'code',
        'number',
        'name',
        'department',
    ]

    form_fields = [
        'code',
        'number',
        'name',
        'department',
    ]

    def configure_grid(self, g):
        super(CategoriesView, self).configure_grid(g)
        g.filters['name'].default_active = True
        g.filters['name'].default_verb = 'contains'
        g.default_sortkey = 'code'
        g.set_link('code')
        g.set_link('number')
        g.set_link('name')


def includeme(config):
    CategoriesView.defaults(config)

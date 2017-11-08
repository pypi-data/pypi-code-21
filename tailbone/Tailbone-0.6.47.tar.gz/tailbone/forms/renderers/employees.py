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
Employee Field Renderers
"""

from __future__ import unicode_literals, absolute_import

import six
from webhelpers2.html import tags

from tailbone.forms.renderers import AutocompleteFieldRenderer


class EmployeeFieldRenderer(AutocompleteFieldRenderer):
    """
    Renderer for :class:`rattail.db.model.Employee` instance fields.
    """
    service_route = 'employees.autocomplete'

    def render_readonly(self, **kwargs):
        employee = self.raw_value
        if not employee:
            return ''
        render_name = kwargs.get('render_name', six.text_type)
        title = render_name(employee)
        if kwargs.get('hyperlink') and self.request.has_perm('employees.view'):
            return tags.link_to(title, self.request.route_url('employees.view', uuid=employee.uuid))
        return title

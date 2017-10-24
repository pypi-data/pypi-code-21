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
User Field Renderers
"""

from __future__ import unicode_literals, absolute_import

import six

from rattail.db import model
from rattail.db.auth import has_permission, administrator_role

import formalchemy
from webhelpers2.html import HTML, tags

from tailbone.db import Session


class UserFieldRenderer(formalchemy.TextFieldRenderer):
    """
    Renderer for :class:`rattail:rattail.db.model.User` instance fields.
    """

    def render_readonly(self, **kwargs):
        user = self.raw_value
        if not user:
            return ''
        title = six.text_type(user)
        if kwargs.get('hyperlink') and self.request.has_perm('users.view'):
            return tags.link_to(title, self.request.route_url('users.view', uuid=user.uuid))
        return title


def PermissionsFieldRenderer(permissions, include_guest=False, include_authenticated=False):

    class PermissionsFieldRenderer(formalchemy.FieldRenderer):

        def deserialize(self):
            perms = []
            i = len(self.name) + 1
            for key in self.params:
                if key.startswith(self.name):
                    perms.append(key[i:])
            return perms

        def _render(self, readonly=False, **kwargs):
            principal = self.field.model
            html = ''
            for groupkey in sorted(permissions, key=lambda k: permissions[k]['label'].lower()):
                inner = HTML.tag('p', c=permissions[groupkey]['label'])
                perms = permissions[groupkey]['perms']
                rendered = False
                for key in sorted(perms, key=lambda p: perms[p]['label'].lower()):
                    checked = has_permission(Session(), principal, key,
                                             include_guest=include_guest,
                                             include_authenticated=include_authenticated)
                    if checked or not readonly:
                        label = perms[key]['label']
                        if readonly:
                            span = HTML.tag('span', c="[X]" if checked else "[ ]")
                            inner += HTML.tag('p', class_='perm', c=span + ' ' + label)
                        else:
                            inner += tags.checkbox(self.name + '-' + key,
                                                   checked=checked, label=label)
                        rendered = True
                if rendered:
                    html += HTML.tag('div', class_='group', c=inner)
            return html or "(none granted)"

        def render(self, **kwargs):
            return self._render(**kwargs)

        def render_readonly(self, **kwargs):
            return self._render(readonly=True, **kwargs)

    return PermissionsFieldRenderer

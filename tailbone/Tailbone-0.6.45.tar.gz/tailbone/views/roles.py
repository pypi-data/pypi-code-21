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
Role Views
"""

from __future__ import unicode_literals, absolute_import

from sqlalchemy import orm

from rattail.db import model
from rattail.db.auth import has_permission, administrator_role, guest_role, authenticated_role

import formalchemy as fa
from formalchemy.fields import IntegerFieldRenderer

from tailbone import forms, grids
from tailbone.db import Session
from tailbone.views.principal import PrincipalMasterView


class RolesView(PrincipalMasterView):
    """
    Master view for the Role model.
    """
    model_class = model.Role
    has_versions = True

    grid_columns = [
        'name',
        'session_timeout',
    ]

    def configure_grid(self, g):
        super(RolesView, self).configure_grid(g)
        g.filters['name'].default_active = True
        g.filters['name'].default_verb = 'contains'
        g.default_sortkey = 'name'
        g.set_link('name')

    def _preconfigure_fieldset(self, fs):
        fs.append(PermissionsField('permissions'))
        permissions = self.request.registry.settings.get('tailbone_permissions', {})
        fs.permissions.set(renderer=forms.renderers.PermissionsFieldRenderer(permissions))
        fs.session_timeout.set(renderer=SessionTimeoutRenderer)
        if (self.viewing or self.editing) and fs.model is guest_role(self.Session()):
            fs.session_timeout.set(readonly=True, attrs={'applicable': False})

    def configure_fieldset(self, fs):
        fs.configure(
            include=[
                fs.name,
                fs.session_timeout,
                fs.permissions,
            ])

    def template_kwargs_view(self, **kwargs):
        role = kwargs['instance']
        if role.users:
            users = sorted(role.users, key=lambda u: u.username)
            actions = [
                grids.GridAction('view', icon='zoomin',
                                 url=lambda r, i: self.request.route_url('users.view', uuid=r.uuid))
            ]
            kwargs['users'] = grids.Grid(None, users, ['username'], request=self.request, model_class=model.User,
                                         main_actions=actions)
        else:
            kwargs['users'] = None
        kwargs['guest_role'] = guest_role(Session())
        kwargs['authenticated_role'] = authenticated_role(Session())
        return kwargs

    def before_delete(self, role):
        admin = administrator_role(Session())
        guest = guest_role(Session())
        authenticated = authenticated_role(Session())
        if role in (admin, guest, authenticated):
            self.request.session.flash("You may not delete the {} role.".format(role.name), 'error')
            return self.redirect(self.request.get_referrer(default=self.request.route_url('roles')))

    def find_principals_with_permission(self, session, permission):
        # TODO: this should search Permission table instead, and work backward to Role?
        all_roles = session.query(model.Role)\
                           .order_by(model.Role.name)\
                           .options(orm.joinedload(model.Role._permissions))
        roles = []
        for role in all_roles:
            if has_permission(session, role, permission):
                roles.append(role)
        return roles


class SessionTimeoutRenderer(IntegerFieldRenderer):

    def render_readonly(self, **kwargs):
        if not kwargs.pop('applicable', True):
            return "(not applicable)"
        return super(SessionTimeoutRenderer, self).render_readonly(**kwargs)


class PermissionsField(fa.Field):
    """
    Custom field for role permissions.
    """

    def sync(self):
        if not self.is_readonly():
            role = self.model
            role.permissions = self.renderer.deserialize()


def includeme(config):
    RolesView.defaults(config)

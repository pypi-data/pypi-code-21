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
"Principal" master view
"""

from __future__ import unicode_literals, absolute_import

import copy

import wtforms

from tailbone.views import MasterView2 as MasterView


class PrincipalMasterView(MasterView):
    """
    Master view base class for security principal models, i.e. User and Role.
    """

    def get_fallback_templates(self, template, mobile=False):
        return [
            '/principal/{}.mako'.format(template),
        ] + super(PrincipalMasterView, self).get_fallback_templates(template, mobile=mobile)

    def find_by_perm(self):
        """
        View for finding all users who have been granted a given permission
        """
        permissions = copy.deepcopy(self.request.registry.settings.get('tailbone_permissions', {}))

        # sort groups, and permissions for each group, for UI's sake
        sorted_perms = sorted(permissions.items(), key=lambda (k, v): v['label'].lower())
        for key, group in sorted_perms:
            group['perms'] = sorted(group['perms'].items(), key=lambda (k, v): v['label'].lower())

        # group options are stable, permission options may depend on submitted group
        group_choices = [(gkey, group['label']) for gkey, group in sorted_perms]
        permission_choices = [('_any_', "(any)")]
        if self.request.method == 'POST':
            if self.request.POST.get('permission_group') in permissions:
                permission_choices.extend([
                    (pkey, perm['label'])
                    for pkey, perm in permissions[self.request.POST['permission_group']]['perms']
                ])

        class PermissionForm(wtforms.Form):
            permission_group = wtforms.SelectField(choices=group_choices)
            permission = wtforms.SelectField(choices=permission_choices)

        principals = None
        form = PermissionForm(self.request.POST)
        if self.request.method == 'POST' and form.validate():
            permission = form.permission.data
            principals = self.find_principals_with_permission(self.Session(), permission)

        context = {'form': form, 'permissions': sorted_perms, 'principals': principals}
        return self.render_to_response('find_by_perm', context)

    @classmethod
    def defaults(cls, config):
        cls._principal_defaults(config)
        cls._defaults(config)

    @classmethod
    def _principal_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        permission_prefix = cls.get_permission_prefix()
        model_title_plural = cls.get_model_title_plural()

        # find principal by permission
        config.add_route('{}.find_by_perm'.format(route_prefix), '{}/find-by-perm'.format(url_prefix))
        config.add_view(cls, attr='find_by_perm', route_name='{}.find_by_perm'.format(route_prefix),
                        permission='{}.find_by_perm'.format(permission_prefix))
        config.add_tailbone_permission(permission_prefix, '{}.find_by_perm'.format(permission_prefix),
                                       "Find all {} with permission X".format(model_title_plural))

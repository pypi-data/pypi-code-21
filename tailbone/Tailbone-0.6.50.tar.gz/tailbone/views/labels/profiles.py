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
Label Profile Views
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model

from pyramid.httpexceptions import HTTPFound

from tailbone import forms
from tailbone.db import Session
from tailbone.views import MasterView2 as MasterView


class ProfilesView(MasterView):
    """
    Master view for the LabelProfile model.
    """
    model_class = model.LabelProfile
    model_title = "Label Profile"
    url_prefix = '/labels/profiles'
    has_versions = True

    grid_columns = [
        'ordinal',
        'code',
        'description',
        'visible',
    ]

    def configure_grid(self, g):
        super(ProfilesView, self).configure_grid(g)
        g.default_sortkey = 'ordinal'
        g.set_type('visible', 'boolean')
        g.set_link('code')
        g.set_link('description')

    def configure_fieldset(self, fs):
        fs.printer_spec.set(renderer=forms.renderers.StrippedTextFieldRenderer)
        fs.formatter_spec.set(renderer=forms.renderers.StrippedTextFieldRenderer)
        fs.format.set(renderer=forms.renderers.CodeTextAreaFieldRenderer)
        fs.configure(
            include=[
                fs.ordinal,
                fs.code,
                fs.description,
                fs.printer_spec,
                fs.formatter_spec,
                fs.format,
                fs.visible,
            ])

    def after_create(self, profile):
        self.after_edit(profile)

    def after_edit(self, profile):
        if not profile.format:
            formatter = profile.get_formatter(self.rattail_config)
            if formatter:
                try:
                    profile.format = formatter.default_format
                except NotImplementedError:
                    pass


def printer_settings(request):
    uuid = request.matchdict['uuid']
    profile = Session.query(model.LabelProfile).get(uuid) if uuid else None
    if not profile:
        return HTTPFound(location=request.route_url('labelprofiles'))

    read_profile = HTTPFound(location=request.route_url(
            'labelprofiles.view', uuid=profile.uuid))

    printer = profile.get_printer(request.rattail_config)
    if not printer:
        request.session.flash("Label profile \"%s\" does not have a functional "
                              "printer spec." % profile)
        return read_profile
    if not printer.required_settings:
        request.session.flash("Printer class for label profile \"%s\" does not "
                              "require any settings." % profile)
        return read_profile

    if request.method == 'POST':
        for setting in printer.required_settings:
            if setting in request.POST:
                profile.save_printer_setting(setting, request.POST[setting])
        return read_profile

    return {'profile': profile, 'printer': printer}


def includeme(config):
    ProfilesView.defaults(config)

    # edit printer settings
    config.add_route('labelprofiles.printer_settings', '/labels/profiles/{uuid}/printer')
    config.add_view(printer_settings, route_name='labelprofiles.printer_settings',
                    renderer='/labels/profiles/printer.mako',
                    permission='labelprofiles.edit')

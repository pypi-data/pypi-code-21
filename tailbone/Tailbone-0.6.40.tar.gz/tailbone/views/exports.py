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
Master class for generic export history views
"""

from __future__ import unicode_literals, absolute_import

import os

from rattail.db import model

import formalchemy as fa
from pyramid.response import FileResponse

from tailbone import forms
from tailbone.views import MasterView2 as MasterView


class ExportMasterView(MasterView):
    """
    Master class for generic export history views
    """
    creatable = False
    editable = False
    export_has_file = False

    grid_columns = [
        'id',
        'created',
        'created_by',
        'record_count',
    ]

    def get_export_key(self):
        if hasattr(self, 'export_key'):
            return self.export_key
        return 

    def get_file_path(self, export, makedirs=False):
        return self.rattail_config.export_filepath(self.export_key,
                                                   export.uuid,
                                                   export.filename,
                                                   makedirs=makedirs)

    def configure_grid(self, g):
        super(ExportMasterView, self).configure_grid(g)

        g.joiners['created_by'] = lambda q: q.join(model.User)
        g.sorters['created_by'] = g.make_sorter(model.User.username)
        g.filters['created_by'] = g.make_filter('created_by', model.User.username)
        g.default_sortkey = 'created'
        g.default_sortdir = 'desc'

        g.set_renderer('id', self.render_id)

        g.set_label('id', "ID")
        g.set_label('created_by', "Created by")

        g.set_link('id')

    def render_id(self, export, column):
        return export.id_str

    def _preconfigure_fieldset(self, fs):
        fs.id.set(label="ID", renderer=forms.renderers.BatchIDFieldRenderer)
        fs.created_by.set(label="Created by", renderer=forms.renderers.UserFieldRenderer,
                          attrs={'hyperlink': True})
        if self.export_has_file and self.viewing:
            download = forms.renderers.FileFieldRenderer.new(
                self, storage_path=self.rattail_config.export_filedir(self.export_key),
                file_path=self.get_file_path(fs.model), download_url=self.get_download_url)
            fs.append(fa.Field('download', renderer=download))

    def configure_fieldset(self, fs):
        fields = [
            fs.id,
            fs.created,
            fs.created_by,
            fs.record_count,
        ]
        if self.export_has_file and self.viewing:
            fields.append(fs.download)
        fs.configure(include=fields)

    def get_download_url(self, filename):
        uuid = self.request.matchdict['uuid']
        return self.request.route_url('{}.download'.format(self.get_route_prefix()), uuid=uuid)

    def download(self):
        """
        View for downloading the export file.
        """
        export = self.get_instance()
        path = self.get_file_path(export)
        response = FileResponse(path, request=self.request)
        response.headers[b'Content-Length'] = str(os.path.getsize(path))
        response.headers[b'Content-Disposition'] = b'attachment; filename="{}"'.format(export.filename)
        return response

    def delete_instance(self, export):
        """
        Delete the export file also, if it exists.
        """
        if self.export_has_file:
            path = self.get_file_path(export)
            if os.path.exists(path):
                os.remove(path)
                os.rmdir(os.path.dirname(path))
        super(ExportMasterView, self).delete_instance(export)

    @classmethod
    def defaults(cls, config):
        """
        Provide default configuration for a master view.
        """
        cls._defaults(config)
        cls._export_defaults(config)

    @classmethod
    def _export_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        permission_prefix = cls.get_permission_prefix()
        model_key = cls.get_model_key()
        model_title = cls.get_model_title()

        # download export file
        if cls.export_has_file:
            config.add_route('{}.download'.format(route_prefix), '{}/{{{}}}/download'.format(url_prefix, model_key))
            config.add_view(cls, attr='download', route_name='{}.download'.format(route_prefix),
                            permission='{}.download'.format(permission_prefix))
            config.add_tailbone_permission(permission_prefix, '{}.download'.format(permission_prefix),
                                           "Download {} data file".format(model_title))

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
Batch Field Renderers
"""

from __future__ import unicode_literals, absolute_import

import os
import stat
import random

import formalchemy as fa
from webhelpers2.html import tags, HTML

from tailbone.forms.renderers import FileFieldRenderer as BaseFileFieldRenderer


class BatchIDFieldRenderer(fa.FieldRenderer):
    """
    Renderer for batch ID fields.
    """
    def render_readonly(self, **kwargs):
        try:
            batch_id = self.raw_value
        except AttributeError:
            # this can happen when creating a new batch, b/c the default value
            # comes from a sequence
            pass
        else:
            if batch_id:
                return '{:08d}'.format(batch_id)
        return ''


class FileFieldRenderer(BaseFileFieldRenderer):
    """
    Custom file field renderer for batches based on a single source data file.
    In edit mode, shows a file upload field.  In readonly mode, shows the
    filename and its size.
    """

    def get_size(self):
        size = super(FileFieldRenderer, self).get_size()
        if size:
            return size
        batch = self.field.parent.model
        path = batch.filepath(self.request.rattail_config, filename=self.field.value)
        if os.path.isfile(path):
            return os.stat(path)[stat.ST_SIZE]
        return 0

    def render(self, **kwargs):
        return BaseFileFieldRenderer.render(self, **kwargs)


class HandheldBatchFieldRenderer(fa.FieldRenderer):
    """
    Renderer for inventory batch's "handheld batch" field.
    """

    def render_readonly(self, **kwargs):
        batch = self.raw_value
        if batch:
            return tags.link_to(
                batch.id_str,
                self.request.route_url('batch.handheld.view', uuid=batch.uuid))
        return ''


class HandheldBatchesFieldRenderer(fa.FieldRenderer):
    """
    Renders a list of associated handheld batches, for a given (presumably
    inventory or labels) batch.
    """

    def render_readonly(self, **kwargs):
        items = ''
        for handheld in self.raw_value:
            text = tags.link_to(handheld.handheld.id_str,
                                self.request.route_url('batch.handheld.view', uuid=handheld.handheld_uuid))
            items += HTML.tag('li', c=text)
        return HTML.tag('ul', c=items)

# -*- coding: utf-8 -*-
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

from formalchemy.ext import fsblob
from formalchemy.fields import FileFieldRenderer as Base


class FileFieldRenderer(fsblob.FileFieldRenderer):
    """
    Custom file field renderer.  In readonly mode, shows a filename and its
    size; in edit mode, supports a single file upload.
    """

    @classmethod
    def new(cls, view, **kwargs):
        name = b'Configured{}_{}'.format(cls.__name__, str(random.random())[2:])
        return type(name, (cls,), dict(view=view, **kwargs))

    @property
    def request(self):
        return self.view.request

    @property
    def storage_path(self):
        return self.view.upload_dir

    def get_file_path(self):
        """
        Returns the absolute path to the data file.
        """
        if hasattr(self, 'file_path'):
            return self.file_path
        return self.field.value

    def get_size(self):
        """
        Returns the size of the data file, in bytes.
        """
        path = self.get_file_path()
        if path and os.path.isfile(path):
            return os.stat(path)[stat.ST_SIZE]
        return 0

    def get_url(self, filename):
        """
        Must return a URL suitable for downloading the file
        """
        url = self.get_download_url()
        if url:
            if callable(url):
                return url(filename)
            return url
        return self.view.get_action_url('download', self.field.parent.model)

    def get_download_url(self):
        if hasattr(self, 'download_url'):
            return self.download_url

    def render(self, **kwargs):
        return Base.render(self, **kwargs)

    def render_readonly(self, **kwargs):
        """
        Render the filename and the binary size in a human readable with a link
        to the file itself.
        """
        value = self.get_file_path()
        if value:
            content = '{} ({})'.format(fsblob.normalized_basename(value),
                                       self.readable_size())
            return fsblob.h.content_tag('a', content,
                                        href=self.get_url(value), **kwargs)
        return ''

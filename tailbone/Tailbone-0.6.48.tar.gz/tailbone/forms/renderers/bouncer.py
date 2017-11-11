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

from __future__ import unicode_literals

import os
import stat
import random

from formalchemy.ext import fsblob


class BounceMessageFieldRenderer(fsblob.FileFieldRenderer):
    """
    Custom file field renderer for email bounce messages.  In readonly mode,
    shows the filename and size.
    """

    @classmethod
    def new(cls, request, handler):
        name = 'Configured%s_%s' % (cls.__name__, unicode(random.random())[2:])
        return type(str(name), (cls,), dict(request=request, handler=handler))

    @property
    def storage_path(self):
        return self.handler.root_msgdir

    def get_size(self):
        size = super(BounceMessageFieldRenderer, self).get_size()
        if size:
            return size
        bounce = self.field.parent.model
        path = os.path.join(self.handler.msgpath(bounce))
        if os.path.isfile(path):
            return os.stat(path)[stat.ST_SIZE]
        return 0

    def get_url(self, filename):
        bounce = self.field.parent.model
        return self.request.route_url('emailbounces.download', uuid=bounce.uuid)

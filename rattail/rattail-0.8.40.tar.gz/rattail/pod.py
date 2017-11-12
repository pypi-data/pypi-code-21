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
`Product Open Data`_ Integration

.. _`Product Open Data`: http://www.product-open-data.com/
"""

from __future__ import unicode_literals, absolute_import

import os


def get_image_path(config, gpc):
    """
    Get an image file path from a product GPC.
    """
    root_path = config.get('rattail.pod', 'pictures.gtin.root_path')
    if root_path:
        gtin = unicode(gpc)[1:]
        return os.path.join(root_path, 'gtin-{}'.format(gtin[:3]), '{}.jpg'.format(gtin))


def get_image_url(config, gpc):
    """
    Get an image URL from a product GPC.
    """
    root_url = config.require('rattail.pod', 'pictures.gtin.root_url')
    root_url = root_url.rstrip('/')
    gtin = unicode(gpc)[1:]
    return u'{0}/gtin-{1}/{2}.jpg'.format(root_url, gtin[:3], gtin)

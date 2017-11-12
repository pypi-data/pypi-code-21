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
Fabric Library for Product Open Data (POD)
"""

from __future__ import unicode_literals
from __future__ import absolute_import

from fabric.api import sudo, cd, env
from fabric.contrib.files import exists

from rattail.fablib import mkdir
from rattail.fablib import apt


def install_pod(path='/srv/pod'):
    """
    Install the Product Open Data (POD) files to the given path.
    """
    apt.install('unzip')
    mkdir(path)
    with cd(path):
        if not exists('pod_pictures_gtin.zip'):
            url = getattr(env, 'setting_pod_download_url',
                          'http://www.product-open-data.com/docs/pod_pictures_gtin_2013.08.29_01.zip')
            sudo('wget --output-document=pod_pictures_gtin.zip {0}'.format(url))
        if not exists('pictures/gtin'):
            sudo('unzip pod_pictures_gtin.zip -d pictures')

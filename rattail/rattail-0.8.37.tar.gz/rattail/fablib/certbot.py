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
Fabric library for Let's Encrypt certbot
"""

from __future__ import unicode_literals, absolute_import

from fabric.api import sudo, cd, abort
from fabric.contrib.files import exists

from rattail.fablib import apt, get_debian_version


def install():
    """
    Install the Let's Encrypt certbot utility
    """
    version = get_debian_version()

    # debian 7 wheezy
    if 7 <= version < 8:
        if not exists('/usr/local/src/certbot'):
            with cd('/usr/local/src'):
                sudo('git clone https://github.com/certbot/certbot')
        sudo('ln --symbolic --force /usr/local/src/certbot/certbot-auto /usr/local/bin/certbot')

    # debian 8 jessie
    elif 8 <= version < 9:
        apt.add_source('deb http://ftp.debian.org/debian jessie-backports main')
        apt.install('python-certbot-apache', target_release='jessie-backports')

    # other..? will have to investigate when this comes up
    else:
        abort("don't know how to install certbot on debian version {}".format(version))


def certonly(*domains):
    """
    Obtain SSL certificates
    """
    domains = ['--domain {}'.format(domain) for domain in domains]
    sudo('certbot certonly --noninteractive --apache {}'.format(' '.join(domains)))

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
Fabric library for Apache web server
"""

from __future__ import unicode_literals, absolute_import

import re

from fabric.api import sudo, abort

from rattail.fablib import apt


def install():
    """
    Install the Apache web service
    """
    apt.install('apache2')


def get_version():
    """
    Fetch the version of Apache running on the target system
    """
    result = sudo('apache2 -v')
    if result.succeeded:
        match = re.match(r'^Server version: Apache/(\d+\.\d+)\.\d+ \(.*\)', result)
        if match:
            return float(match.group(1))


def install_wsgi(python_home=None):
    """
    Install the mod_wsgi Apache module, with optional ``WSGIPythonHome`` value.
    """
    apt.install('libapache2-mod-wsgi')
    if python_home:
        if get_version() == 2.2:
            sudo('echo WSGIPythonHome {} > /etc/apache2/conf.d/wsgi'.format(python_home))
        else: # assuming 2.4
            sudo('echo WSGIPythonHome {} > /etc/apache2/conf-available/wsgi.conf'.format(python_home))
            enable_conf('wsgi')


def enable_conf(*names):
    """
    Enable the given Apache configurations
    """
    for name in names:
        sudo('a2enconf {}'.format(name))


def enable_mod(*names):
    """
    Enable the given Apache modules
    """
    for name in names:
        sudo('a2enmod {}'.format(name))


def enable_site(*names):
    """
    Enable the given Apache site(s)
    """
    for name in names:
        sudo('a2ensite {}'.format(name))


def deploy_conf(deployer, local_path, name, enable=False):
    """
    Deploy a config snippet file to Apache
    """
    version = get_version()
    if version == 2.2:
        deployer(local_path, '/etc/apache2/conf.d/{}.conf'.format(name))
    else:
        deployer(local_path, '/etc/apache2/conf-available/{}.conf'.format(name))
        if enable:
            enable_conf(name)


def deploy_site(deployer, local_path, name, enable=False, **kwargs):
    """
    Deploy a file to Apache sites-available
    """
    apache_version = get_version()
    if apache_version == 2.2:
        path = '/etc/apache2/sites-available/{}'.format(name)
    else:
        path = '/etc/apache2/sites-available/{}.conf'.format(
            '000-default' if name == 'default' else name)
    context = kwargs.pop('context', {})
    context['apache_version'] = apache_version
    deployer(local_path, path, context=context, **kwargs)
    if enable and name != 'default':
        enable_site(name)


def restart():
    """
    Restart the Apache web service
    """
    sudo('service apache2 restart')


def start():
    """
    Start the Apache web service
    """
    sudo('service apache2 start')


def stop():
    """
    Stop the Apache web service
    """
    sudo('service apache2 stop')

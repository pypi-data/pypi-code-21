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
Fabric library for Postfix
"""

from __future__ import unicode_literals, absolute_import

from fabric.api import sudo
from fabric.contrib.files import sed, append


from rattail.fablib import apt


def install():
    """
    Install the Postfix mail service
    """
    apt.install('postfix')
    apt.purge('exim4', 'exim4-base', 'exim4-config', 'exim4-daemon-light')


def alias(name, alias_to, path='/etc/aliases'):
    """
    Set a mail alias for Postfix
    """
    # replace setting if already exists; then add in case it didn't
    entry = '{}: {}'.format(name, alias_to)
    sed(path, r'^{}: .*$'.format(name), entry, use_sudo=True)
    append(path, entry, use_sudo=True)
    sudo('newaliases')


def restart():
    """
    Restart the Postfix mail service
    """
    sudo('service postfix restart')


def set_config(setting, value, path='/etc/postfix/main.cf'):
    """
    Configure the given setting with the given value.
    """
    # replace setting if already exists; then add in case it didn't
    entry = '{} = {}'.format(setting, value)
    sed(path, r'^{} = .*$'.format(setting), entry, use_sudo=True)
    append(path, entry, use_sudo=True)


def set_myhostname(hostname):
    """
    Configure the 'myhostname' setting with the given string.
    """
    set_config('myhostname', hostname)


def set_mydestination(*destinations):
    """
    Configure the 'mydestinations' setting with the given strings.
    """
    set_config('mydestination', ', '.join(destinations))


def set_mynetworks(*networks):
    """
    Configure the 'mynetworks' setting with the given strings.
    """
    set_config('mynetworks', ' '.join(networks))


def set_relayhost(relayhost):
    """
    Configure the 'relayhost' setting with the given string
    """
    set_config('relayhost', relayhost)

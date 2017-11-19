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
Fabric library for the APT package system
"""

from __future__ import unicode_literals, absolute_import

from fabric.api import sudo, settings
from fabric.contrib.files import append

from rattail.fablib import make_deploy, get_debian_version, get_ubuntu_version


deploy = make_deploy(__file__)


def install(*packages, **kwargs):
    """
    Install one or more packages via ``apt-get install``.
    """
    frontend = kwargs.get('frontend', 'noninteractive')
    target = kwargs.get('target_release')
    target = '--target-release={}'.format(target) if target else ''
    force_yes = ' --force-yes' if kwargs.get('force_yes') else ''
    sudo('DEBIAN_FRONTEND={} apt-get --assume-yes {}{} install {}'.format(
            frontend, target, force_yes, ' '.join(packages)))


def purge(*packages):
    """
    Uninstall and purge config for given packages
    """
    sudo('apt-get --assume-yes purge {}'.format(' '.join(packages)))


def update():
    """
    Perform an ``apt-get update`` operation.
    """
    sudo('apt-get update')


def add_repository(repo):
    """
    Add a new APT repository
    """
    sudo('add-apt-repository --yes {}'.format(repo))
    update()


def add_source(entry):
    """
    Add a new entry to the apt/sources.list file
    """
    append('/etc/apt/sources.list', entry, use_sudo=True)
    update()


def dist_upgrade(frontend='noninteractive'):
    """
    Perform a full ``apt-get dist-upgrade`` operation.
    """
    update()
    sudo('DEBIAN_FRONTEND={} apt-get --assume-yes dist-upgrade'.format(frontend))


def configure_listchanges():
    """
    Configure apt listchanges to never use a frontend.
    """
    deploy('apt/listchanges.conf', '/etc/apt/listchanges.conf')


def install_emacs():
    """
    Install the Emacs editor
    """
    with settings(warn_only=True):
        result = sudo('which emacs')
    if result.succeeded:
        return

    emacs = 'emacs-nox'
    debian_version = get_debian_version()
    if debian_version:
        if debian_version < 8:
            emacs = 'emacs23-nox'
    else:
        ubuntu_version = get_ubuntu_version()
        if ubuntu_version and ubuntu_version < 16:
            emacs = 'emacs23-nox'

    install(emacs, 'emacs-goodies-el')

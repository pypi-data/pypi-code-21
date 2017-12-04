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
Fabric Library for SSH
"""

from __future__ import unicode_literals, absolute_import

import warnings

from fabric.api import sudo, cd, settings
from fabric.contrib.files import exists, sed, append

from rattail.fablib import mkdir, agent_sudo
from rattail.fablib.python import cdvirtualenv


def cache_host_key(host, for_user='root', with_agent=False, warn_only=True, identity=''):
    """
    Cache the SSH host key for the given host, for the given user.
    """
    user = None if for_user == 'root' else for_user
    _sudo = agent_sudo if with_agent else sudo
    if identity:
        identity = '-i {}'.format(identity)
    cmd = 'ssh {} -o StrictHostKeyChecking=no {} echo'.format(identity, host)
    if warn_only:
        with settings(warn_only=True):
            _sudo(cmd, user=user)
    else:
        _sudo(cmd, user=user)


def uncache_host_key(host, for_user='root'):
    """
    Remove the cached SSH host key for the given host, for the given user.
    """
    user = None if for_user == 'root' else for_user
    sudo('ssh-keygen -R {}'.format(host), user=user)


def restart():
    """
    Restart the OpenSSH service
    """
    sudo('service ssh restart')


def configure(allow_root=False):
    """
    Configure the OpenSSH service
    """
    path = '/etc/ssh/sshd_config'
    value = 'without-password' if allow_root else 'no'
    sed(path, r'^PermitRootLogin\s+.*', 'PermitRootLogin {}'.format(value), use_sudo=True)
    entry = 'PasswordAuthentication no'
    sed(path, r'^PasswordAuthentication\s+.*', entry, use_sudo=True)
    append(path, entry, use_sudo=True)
    restart()


def configure_ssh(restrict_root=True):
    warnings.warn("Function `ssh.configure_ssh()` is deprecated, please "
                  "use `ssh.configure()` instead.", DeprecationWarning)
    return configure(allow_root=not restrict_root)


def establish_identity(envname, comment, user='rattail', home='/var/lib/rattail'):
    """
    Generate a SSH key pair and configure it for local use.
    """
    home = home.rstrip('/')
    sshdir = '{0}/.ssh'.format(home)
    owner='{0}:{0}'.format(user)
    mkdir(sshdir, owner=owner, mode='0700')
    with cd(sshdir):
        if not exists('authorized_keys'):
            sudo('touch authorized_keys')
        sudo('chown {0} authorized_keys'.format(owner))
        sudo('chmod 0600 authorized_keys')
    with cdvirtualenv(envname, 'app'):
        mkdir('ssh', owner=owner, mode='0700')
    with cdvirtualenv(envname, 'app/ssh'):
        if not exists('id_rsa', use_sudo=True):
            sudo("ssh-keygen -C '{0}' -P '' -f id_rsa".format(comment))
            sudo('cat id_rsa.pub >> {0}/authorized_keys'.format(sshdir))
        sudo('chown {0} id_rsa*'.format(owner))

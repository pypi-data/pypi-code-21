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
Fabric library for Rattail itself
"""

from __future__ import unicode_literals
from __future__ import absolute_import

from fabric.api import sudo, env, cd

from rattail.fablib import make_deploy, make_system_user, mkdir


deploy = make_deploy(__file__)


def bootstrap_rattail(home='/var/lib/rattail', uid=None, shell='/bin/bash'):
    """
    Bootstrap a basic Rattail software environment.
    """
    make_system_user('rattail', home=home, uid=uid, shell=shell)
    sudo('adduser {0} rattail'.format(env.user))

    mkdir('/etc/rattail')
    mkdir('/srv/rattail')
    mkdir('/var/log/rattail', owner='rattail:rattail', mode='0775')

    mkdir('/srv/rattail/init')
    deploy('daemon', '/srv/rattail/init/daemon')
    deploy('check-rattail-daemon', '/usr/local/bin/check-rattail-daemon')
    deploy('soffice', '/srv/rattail/init/soffice')
    # TODO: deprecate / remove these
    deploy('bouncer', '/srv/rattail/init/bouncer')
    deploy('datasync', '/srv/rattail/init/datasync')
    deploy('filemon', '/srv/rattail/init/filemon')


def upgrade_rattail_db(envname=None, envpath=None, config=None, user='rattail'):
    """
    Upgrade a Rattail database in the "default" supported way
    """
    if not (envname or envpath):
        raise ValueError("Must specify value for either 'envname' or 'envpath'")
    if not envpath:
        envpath = '/srv/envs/{}'.format(envname)
    if not config:
        config = 'app/rattail.conf'
    with cd(envpath):
        sudo('bin/alembic --config {} upgrade heads'.format(config), user=user)


def deploy_rattail_sudoers(remote_path='/etc/sudoers.d/rattail'):
    """
    Deploy the common sudoers file for rattail.
    """
    deploy.sudoers('sudoers', remote_path)

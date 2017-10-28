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
Fabric library for CORE-POS (IS4C)
"""

from __future__ import unicode_literals, absolute_import

import webbrowser

from fabric.api import sudo, cd, env, run
from fabric.contrib.files import exists

from rattail.fablib import apt, mysql, mkdir


def install_fannie(rootdir, branch='version-2.3', first_time=None, url=None):
    """
    Install the Fannie app to the given location
    """
    if first_time is None:
        first_time = not exists(rootdir)
    mkdir(rootdir)
    with cd(rootdir):

        # fannie source
        if not exists('IS4C'):
            sudo('git clone https://github.com/CORE-POS/IS4C.git')
            with cd('IS4C'):
                sudo('git checkout {}'.format(branch))
        with cd('IS4C'):
            sudo('git pull')

        # composer
        if not exists('composer.phar'):
            sudo('curl -sS https://getcomposer.org/installer | php')
        mkdir('/var/www/.composer', owner='www-data')

        # fannie dependencies
        with cd('IS4C'):
            mkdir(['vendor', 'fannie/src/javascript/composer-components'], owner='www-data')
            sudo('../composer.phar install', user='www-data')

        # shadowread
        with cd('IS4C/fannie/auth/shadowread'):
            sudo('make')
            sudo('make install')

        # fannie config
        with cd('IS4C/fannie'):
            if not exists('config.php'):
                sudo('cp config.php.dist config.php')
                sudo('chown root:www-data config.php')
                sudo('chmod 0660 config.php')

        # fannie logging
        with cd('IS4C/fannie/logs'):
            for name in ['fannie', 'debug_fannie', 'queries', 'php-errors', 'dayend']:
                sudo('touch {}.log'.format(name))
                sudo('chown www-data:www-data {}.log'.format(name))

    # fannie databases
    mysql.create_user('is4c', host='%', password='is4c')
    mysql.create_db('core_op', user="is4c@'%'")
    mysql.create_db('core_trans', user="is4c@'%'")
    mysql.create_db('trans_archive', user="is4c@'%'")

    # fannie web installer
    if first_time:
        url = url or getattr(env, 'fannie_rooturl', 'http://localhost/fannie/')
        webbrowser.open_new_tab('{}/install/'.format(url.rstrip('/')))

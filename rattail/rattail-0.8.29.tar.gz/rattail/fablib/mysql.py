# -*- coding: utf-8; -*-
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
Fabric Library for MySQL
"""

from __future__ import unicode_literals, absolute_import

from fabric.api import sudo, hide, get, put, abort, local, run
from fabric.contrib.files import sed

from rattail.fablib import apt, make_deploy


deploy = make_deploy(__file__)


def install(password):
    """
    Install the MySQL database service
    """
    deploy('mysql/debconf.mako', 'debconf', context={'password': password})
    sudo('debconf-set-selections debconf')
    sudo('rm debconf')
    apt.install('mysql-server')
    deploy('mysql/my.cnf.mako', '/root/.my.cnf', mode='0600', context={'password': password})


def is_mariadb():
    """
    Returns boolean indicating if MySQL server is actually MariaDB.
    """
    if "MariaDB" in run('mysql --version'):
        return True
    return False


def restart():
    """
    Restart the MySQL database service
    """
    sudo('service mysql restart')


def set_bind_address(address):
    """
    Configure the 'bind-address' setting with the given value.
    """
    sed('/etc/mysql/my.cnf', '^bind-address.*', 'bind-address = {}'.format(address), use_sudo=True)


def user_exists(name, host='localhost'):
    """
    Determine if a given MySQL user exists.
    """
    user = sql("SELECT User FROM user WHERE User = '{0}' and Host = '{1}'".format(name, host), database='mysql')
    return user == name


def create_user(name, host='localhost', password=None, checkfirst=True):
    """
    Create a MySQL user account.
    """
    if not checkfirst or not user_exists(name, host):
        sql("CREATE USER '{0}'@'{1}';".format(name, host))
    if password:
        with hide('running'):
            sql("SET PASSWORD FOR '{0}'@'{1}' = PASSWORD('{2}');".format(
                name, host, password))


def drop_user(name, host='localhost'):
    """
    Drop a MySQL user account.
    """
    sql("drop user '{0}'@'{1}'".format(name, host))
    

def db_exists(name):
    """
    Determine if a given MySQL database exists.
    """
    db = sql("SELECT SCHEMA_NAME FROM SCHEMATA WHERE SCHEMA_NAME = '{0}'".format(name), database='information_schema')
    return db == name


def table_exists(name, database):
    """
    Determine if a given table exists within the given MySQL database.
    """
    table = sql("SELECT TABLE_NAME FROM TABLES WHERE TABLE_SCHEMA = '{0}' AND TABLE_NAME = '{1}'".format(database, name), database='information_schema')
    return table == name


def create_db(name, checkfirst=True, user=None):
    """
    Create a MySQL database.
    """
    if not checkfirst or not db_exists(name):
        sudo('mysqladmin create {0}'.format(name))
        if user:
            grant_access(name, user)


def drop_db(name, checkfirst=True):
    """
    Drop a MySQL database.
    """
    if not checkfirst or db_exists(name):
        sudo('mysqladmin drop --force {0}'.format(name))


def grant_access(dbname, username):
    """
    Grant full access to the given database for the given user.  Note that the
    username should be given in MySQL's native format, e.g. 'myuser@localhost'.
    """
    sql('grant all on `{0}`.* to {1}'.format(dbname, username))


def sql(sql, database=''):
    """
    Execute some SQL.
    """
    # some crazy quoting required here, see also
    # http://stackoverflow.com/a/1250279
    sql = sql.replace("'", "'\"'\"'")
    return sudo("mysql --execute='{}' --batch --skip-column-names {}".format(sql, database))


def download_db(name, destination=None):
    """
    Download a database from the "current" server.
    """
    if destination is None:
        destination = './{0}.sql.gz'.format(name)
    sudo('mysqldump --result-file={0}.sql {0}'.format(name))
    sudo('gzip --force {0}.sql'.format(name))
    get('{0}.sql.gz'.format(name), destination)
    sudo('rm {0}.sql.gz'.format(name))


def restore_db(name, source=None, user=None):
    """
    Upload and restore a database to the current server
    """
    if not source:
        source = '{}.sql.gz'.format(name)
    put(source, '{}.sql.gz'.format(name))
    sudo('gunzip --force {}.sql.gz'.format(name))
    drop_db(name)
    create_db(name, user=user)
    sudo('mysql --execute="source {0}.sql" {0}'.format(name))
    sudo('rm {}.sql'.format(name))


def clone_db(name, download, force=False):
    """
    Clone a MySQL database from a (presumably live) server

    :param name: Name of the database.

    :param force: Whether the target database should be forcibly dropped, if it
       exists already.
    """
    if db_exists(name):
       if force:
           drop_db(name, checkfirst=False)
       else:
           abort("Database '{}' already exists! (pass force=true to override)".format(name))

    create_db(name, checkfirst=False)

    # obtain database dump from live server
    download()

    # upload database dump to target server
    put('{}.sql.gz'.format(name))
    local('rm {}.sql.gz'.format(name))

    # restore database on target server
    run('gunzip --force {}.sql.gz'.format(name))
    sudo('mysql {0} < {0}.sql'.format(name))
    run('rm {}.sql'.format(name))

# mosaiq_connection
# Copyright (C) 2017  CCA Health Care

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""A toolbox for connecting to Mosaiq SQL.
"""

import time
import warnings
from getpass import getpass

import pymssql
import keyring

from IPython.display import display, Markdown

def single_connect(user, server):
    """Connect to the Mosaiq server.
    Ask the user for a password if they haven't logged in before.
    """
    password = keyring.get_password(server, user)
    if password is None:
        display(Markdown(
            "### Provide password for '{}' server and '{}' user".format(
                server, user)))
        password = getpass()
        keyring.set_password(server, user, password)

    try:
        conn = pymssql.connect(server, user, password, 'MOSAIQ')
    except:
        time.sleep(1)
        conn = pymssql.connect(server, user, password, 'MOSAIQ')

    return conn, conn.cursor()


def multi_connect(users, sql_servers):
    """Create SQL connections and cursors.
    """
    connections = dict()
    cursors = dict()

    for key, server in sql_servers.items():
        connections[key], cursors[key] = single_connect(users[key], server)

    return connections, cursors


def single_close(connection):
    connection.close()


def multi_close(connections):
    """Close the SQL connections.
    """
    for _, item in connections.items():
        single_close(item)


class multi_mosaiq_connect():
    """A controlled execution class that opens and closes multiple SQL
    connections.
    """
    def __init__(self, users, sql_servers):
        self.users = users
        self.sql_servers = sql_servers
    def __enter__(self):
        self.connections, cursors = multi_connect(
            self.users, self.sql_servers)
        return cursors
    def __exit__(self, type, value, traceback):
        multi_close(self.connections)


def sql_connection(*args, **kwargs):
    warnings.warn(
        "sql_connection is deprecated in favour of mult_mosaiq_connect",
        DeprecationWarning)
    return multi_mosaiq_connect(*args, **kwargs)


class mosaiq_connect():
    """A controlled execution class that opens and closes a single SQL
    connection to mosaiq.
    """
    def __init__(self, user, sql_server):
        self.user = user
        self.sql_server = sql_server
    def __enter__(self):
        self.connection, cursor = single_connect(
            self.user, self.sql_server)
        return cursor
    def __exit__(self, type, value, traceback):
        single_close(self.connection)
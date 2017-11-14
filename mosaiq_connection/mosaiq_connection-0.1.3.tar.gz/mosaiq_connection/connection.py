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
from getpass import getpass

import pymssql
import keyring

from IPython.display import display, Markdown

def _connect(user, server):
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
        try:
            conn = pymssql.connect(server, user, password, 'MOSAIQ')
        except:
            print('Unable to connect to {}, skipping connection'.format(
                server))
            return None, None

    return conn, conn.cursor()


def _create_cursors(users, sql_servers):
    """Create SQL connections and cursors.
    """
    connections = dict()
    cursors = dict()

    for key, server in sql_servers.items():
        connections[key], cursors[key] = _connect(users[key], server)
        if connections[key] is None:
            connections.pop(key)
            cursors.pop(key)

    return connections, cursors


def _close_connections(connections):
    """Close the SQL connections.
    """
    for _, item in connections.items():
        item.close()


class sql_connection():
    """A controlled execution class that opens and closes SQL connections.
    """
    def __init__(self, users, sql_servers):
        self.users = users
        self.sql_servers = sql_servers
    def __enter__(self):
        self.connections, cursors = _create_cursors(
            self.users, self.sql_servers)
        return cursors
    def __exit__(self, type, value, traceback):
        _close_connections(self.connections)
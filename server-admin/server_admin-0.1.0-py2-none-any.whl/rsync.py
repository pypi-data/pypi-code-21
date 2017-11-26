u"""
Copyright 2017 Hermann Krumrey

This file is part of server-admintools.

server-admintools is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

server-admintools is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with server-admintools.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import
import argparse
from subprocess import Popen

u"""
This module contains functions that help manage rsync backups
"""


def execute_ssh_rsync_backup(
        user, source_server, source_path, destination, port=22):
    u"""
    Executes an rsync backup over SSH
    :param user: The user that logs on using SSH
    :param source_server: The source server name/IP address
    :param source_path: The path on the source machine
    :param destination: The path on the destination machine
    :param port: The port over which to connect, defaults to 22
    :return: None
    """

    Popen([
        u"rsync", u"-av",
        user + u"@" + source_server + u":" + source_path,
        destination,
        u"-e", u"ssh -p " + unicode(port)
    ]).wait()


def parse_ssh_rsync_backup_args():
    u"""
    Parses the CLI for the information required for an Rsync backup
    :return: None
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(u"-u", u"--user", required=True,
                        help=u"The user on the source system")
    parser.add_argument(u"-d", u"--destination", required=True,
                        help=u"The destination path to where to back up to")
    parser.add_argument(u"-s", u"--source", required=True,
                        help=u"The source path to back up")
    parser.add_argument(u"-i", u"--server", required=True,
                        help=u"The server to connect to")
    parser.add_argument(u"-p", u"--port", default=22, type=int,
                        help=u"Specifies a non-standard SSH port")
    return parser.parse_args()


def run_ssh_rsync_backup():
    u"""
    Runs the Rsync backup using the CLI data
    :return: None
    """

    args = parse_ssh_rsync_backup_args()
    execute_ssh_rsync_backup(
        args.user,
        args.server,
        args.source,
        args.destination,
        args.port
    )

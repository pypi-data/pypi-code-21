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
import os
import shutil
import argparse
from subprocess import Popen
from datetime import datetime
from server_admintools.sudo import quit_if_not_sudo, change_ownership

u"""
This module contains functions that help manage gitlab backups
"""


def parse_backup_args():
    u"""
    Parses the arguments for the gitlab-backup script
    :return: The arguments provided via the CLI
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(u"-d", u"--destination",
                        default=u"/var/opt/gitlab/backups",
                        help=u"Destination of the backup file")
    parser.add_argument(u"-b", u"--backup-path",
                        default=u"/var/opt/gitlab/backups",
                        help=u"The backup directory as specified in gitlab.rb")
    parser.add_argument(u"-u", u"--user",
                        default=u"root",
                        help=u"The user that should own the backup file. "
                             u"Defaults to root.")
    args = parser.parse_args()

    return {
        u"destination": args.destination,
        u"backup_path": args.backup_path,
        u"user": args.user
    }


def execute_gitlab_rake_backup():
    u"""
    Executes the gitlab-rake command that creates a backup file in the
    location specified in the gitlab.rb config file
    :return: None
    """
    print u"Executing gitlab-rake backup"
    Popen([u"gitlab-rake", u"gitlab:backup:create"]).wait()


def create_config_tarball(destination_file):
    u"""
    Creates a tarball containing the gitlab instance's secrets and config
    :return: None
    """
    print u"Creating gitlab config and secrets backup"
    Popen([u"tar", u"zcf", destination_file, u"/etc/gitlab"])


def create_backup():
    u"""
    Performs the Gitlab Backup. Requires sudo permissions.
    After creating and renaming the backup, changes the ownership to the
    specified user
    :return: None
    """
    quit_if_not_sudo()
    args = parse_backup_args()

    before = os.listdir(args[u"backup_path"])
    execute_gitlab_rake_backup()
    after = os.listdir(args[u"backup_path"])

    backups = []
    for x in after:
        if x not in before:
            backups.append(x)

    if len(backups) != 1:
        print u"More than one backup generated. Aborting."

    source_path = os.path.join(args[u"backup_path"], backups[0])
    date_string = datetime.today().strftime(u"%Y-%m-%d-%H-%M-%S")
    dest_filename = date_string + u"_gitlab.tar"
    tar_filename = date_string + u"_gitlab_secrets.tar"
    dest_path = os.path.join(args[u"destination"], dest_filename)
    tar_path = os.path.join(args[u"destination"], tar_filename)

    if not os.path.exists(args[u"destination"]):
        os.makedirs(args[u"destination"])

    os.rename(source_path, dest_path)
    create_config_tarball(tar_path)
    change_ownership(dest_path, args[u"user"])
    change_ownership(tar_path, args[u"user"])

    print u"Backup completed.\n"
        u"Rights transferred to " + args[u"user"] + u".\n"
        u"Location:" + args[u"destination"]


def parse_clone_repo_args():
    u"""
    Parses the arguments for the git repository cloner
    :return: The parsed CLI arguments
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(u"-t", u"--token", required=True,
                        help=u"The Gitlab API Access token")
    parser.add_argument(u"-s", u"--server", required=True,
                        help=u"The Gitlab Server address")
    parser.add_argument(u"-d", u"--destination", required=True,
                        help=u"The backup destination")
    return parser.parse_args()


def fetch_gitlab_clone_script():
    u"""
    Downloads the latest version of the gitlab-cloner script
    :return: None
    """

    if os.path.isdir(u"gitlab-cloner"):
        shutil.rmtree(u"gitlab-cloner")
    Popen([u"git", u"clone",
           u"https://gitlab.namibsun.net/namboy94/gitlab-cloner.git"]).wait()


def backup_repos():
    u"""
    Clones all repositories from a gitlab instance for a user and tars the
    directories together
    :return: None
    """

    args = parse_clone_repo_args()
    fetch_gitlab_clone_script()

    date_string = datetime.today().strftime(u"%Y-%m-%d-%H-%M-%S")
    dest_path = os.path.join(args.destination, date_string + u"_git_repos")
    Popen([u"python", u"gitlab-cloner/gitlab-cloner.py",
           args.server, args.token, u"-d", dest_path, u"-a"
           ]).wait()
    Popen([u"tar", u"zcf", dest_path + u".tar", dest_path]).wait()
    shutil.rmtree(dest_path)

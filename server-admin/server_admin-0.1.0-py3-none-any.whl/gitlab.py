"""
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

import os
import shutil
import argparse
from subprocess import Popen
from datetime import datetime
from server_admintools.sudo import quit_if_not_sudo, change_ownership

"""
This module contains functions that help manage gitlab backups
"""


def parse_backup_args():
    """
    Parses the arguments for the gitlab-backup script
    :return: The arguments provided via the CLI
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--destination",
                        default="/var/opt/gitlab/backups",
                        help="Destination of the backup file")
    parser.add_argument("-b", "--backup-path",
                        default="/var/opt/gitlab/backups",
                        help="The backup directory as specified in gitlab.rb")
    parser.add_argument("-u", "--user",
                        default="root",
                        help="The user that should own the backup file. "
                             "Defaults to root.")
    args = parser.parse_args()

    return {
        "destination": args.destination,
        "backup_path": args.backup_path,
        "user": args.user
    }


def execute_gitlab_rake_backup():
    """
    Executes the gitlab-rake command that creates a backup file in the
    location specified in the gitlab.rb config file
    :return: None
    """
    print("Executing gitlab-rake backup")
    Popen(["gitlab-rake", "gitlab:backup:create"]).wait()


def create_config_tarball(destination_file):
    """
    Creates a tarball containing the gitlab instance's secrets and config
    :return: None
    """
    print("Creating gitlab config and secrets backup")
    Popen(["tar", "zcf", destination_file, "/etc/gitlab"])


def create_backup():
    """
    Performs the Gitlab Backup. Requires sudo permissions.
    After creating and renaming the backup, changes the ownership to the
    specified user
    :return: None
    """
    quit_if_not_sudo()
    args = parse_backup_args()

    before = os.listdir(args["backup_path"])
    execute_gitlab_rake_backup()
    after = os.listdir(args["backup_path"])

    backups = []
    for x in after:
        if x not in before:
            backups.append(x)

    if len(backups) != 1:
        print("More than one backup generated. Aborting.")

    source_path = os.path.join(args["backup_path"], backups[0])
    date_string = datetime.today().strftime("%Y-%m-%d-%H-%M-%S")
    dest_filename = date_string + "_gitlab.tar"
    tar_filename = date_string + "_gitlab_secrets.tar"
    dest_path = os.path.join(args["destination"], dest_filename)
    tar_path = os.path.join(args["destination"], tar_filename)

    if not os.path.exists(args["destination"]):
        os.makedirs(args["destination"])

    os.rename(source_path, dest_path)
    create_config_tarball(tar_path)
    change_ownership(dest_path, args["user"])
    change_ownership(tar_path, args["user"])

    print(
        "Backup completed.\n"
        "Rights transferred to " + args["user"] + ".\n"
        "Location:" + args["destination"]
    )


def parse_clone_repo_args():
    """
    Parses the arguments for the git repository cloner
    :return: The parsed CLI arguments
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--token", required=True,
                        help="The Gitlab API Access token")
    parser.add_argument("-s", "--server", required=True,
                        help="The Gitlab Server address")
    parser.add_argument("-d", "--destination", required=True,
                        help="The backup destination")
    return parser.parse_args()


def fetch_gitlab_clone_script():
    """
    Downloads the latest version of the gitlab-cloner script
    :return: None
    """

    if os.path.isdir("gitlab-cloner"):
        shutil.rmtree("gitlab-cloner")
    Popen(["git", "clone",
           "https://gitlab.namibsun.net/namboy94/gitlab-cloner.git"]).wait()


def backup_repos():
    """
    Clones all repositories from a gitlab instance for a user and tars the
    directories together
    :return: None
    """

    args = parse_clone_repo_args()
    fetch_gitlab_clone_script()

    date_string = datetime.today().strftime("%Y-%m-%d-%H-%M-%S")
    dest_path = os.path.join(args.destination, date_string + "_git_repos")
    Popen(["python", "gitlab-cloner/gitlab-cloner.py",
           args.server, args.token, "-d", dest_path, "-a"
           ]).wait()
    Popen(["tar", "zcf", dest_path + ".tar", dest_path]).wait()
    shutil.rmtree(dest_path)

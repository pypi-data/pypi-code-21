# -*- mode: python; encoding: utf-8 -*-
#
# Copyright 2017 the Critic contributors, Opera Software ASA
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License.  You may obtain a copy of
# the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations under
# the License.

import distutils.spawn
import grp
import json
import logging
import os
import psycopg2
import pwd
import subprocess
import sys

logger = logging.getLogger(__name__)

import api
import base
import data

name = "install"
description = "Install the base Critic system."
allow_missing_configuration = True

SCHEMA_FILES = [
    # No dependencies.
    "dbschema/base.sql",
    "dbschema/users.sql",

    # Depends on: base[files].
    "dbschema/git.sql",

    # Depends on: users.
    "dbschema/news.sql",

    # Depends on: git, users.
    "dbschema/trackedbranches.sql",

    # Depends on: base[files], git.
    "dbschema/changesets.sql",

    # Depends on: git, users.
    "dbschema/filters.sql",

    # Depends on: git, users, filters.
    "dbschema/preferences.sql",

    # Depends on: base[files], git, users, changesets.
    "dbschema/reviews.sql",

    # Depends on: base[files], git, users, reviews.
    "dbschema/comments.sql",

    # Depends on: base[files], git, users, reviews.
    "dbschema/extensions.sql",
]

PGSQL_FILES = ["dbschema/comments.pgsql"]

def get_hostname():
    try:
        return subprocess.check_output(
            ["hostname", "--fqdn"], encoding="utf-8").strip()
    except subprocess.CalledProcessError:
        return None

def is_quickstarted():
    return os.environ.get("CRITIC_QUICKSTART") == str(os.getpgrp())

def get_home_dir():
    if sys.prefix != sys.base_prefix:
        return sys.prefix
    return "/var/lib/critic"

def get_settings_dir():
    return base.settings_dir()

def get_runtime_dir():
    if is_quickstarted():
        return os.path.join(sys.prefix, "run")
    return "/var/run/critic"

def get_logs_dir():
    if is_quickstarted():
        return os.path.join(sys.prefix, "log")
    return "/var/log/critic"

def get_cache_dir():
    if is_quickstarted():
        return os.path.join(sys.prefix, "cache")
    return "/var/cache/critic"

def get_repositories_dir():
    if is_quickstarted():
        return os.path.join(sys.prefix, "git")
    return "/var/git"

def ensure_dir(path, *, uid, gid, mode=0o755, force_attributes=True):
    update_attributes = force_attributes
    if not os.path.isdir(path):
        ensure_dir(os.path.dirname(path), uid=0, gid=0, force_attributes=False)
        logger.info("Creating directory: %s", path)
        os.mkdir(path)
        update_attributes = True
    if update_attributes:
        os.chmod(path, mode)
        os.chown(path, uid, gid)

PSQL_EXECUTABLE = None

def psql_argv(*, arguments=None, database=None):
    argv = [PSQL_EXECUTABLE, "-v", "ON_ERROR_STOP=1"]
    if arguments is not None:
        if arguments.database_host:
            argv.extend([
                "-h", arguments.database_host,
                "-p", str(arguments.database_port),
                "-U", arguments.database_username,
            ])
        if arguments.database_password:
            argv.extend([
                "-W", arguments.database_password
            ])
    if database is not None:
        argv.extend(["-d", database])
    return argv

def psql(command, *, database=None, arguments=None, username="postgres"):
    from . import as_user
    argv = psql_argv(arguments=arguments, database=database)
    argv.extend(["-c", command])
    with as_user(name=username):
        subprocess.check_output(argv, stderr=subprocess.STDOUT)

def psql_list_roles(arguments):
    from . import as_user
    argv = psql_argv(arguments=arguments)
    argv.extend([
        "--no-align", "--tuples-only",
        "-c", "SELECT rolname FROM pg_roles"
    ])
    with as_user(name="postgres"):
        return subprocess.check_output(argv).decode().splitlines()

class SQLScript():
    def __init__(self, script_source):
        self.commands = []
        command = []
        quotes = []
        for line in script_source.splitlines():
            fragment, _, comment = line.strip().partition("--")
            fragment = fragment.strip()
            if not fragment:
                continue
            command.append(fragment)
            if fragment == "$$":
                if quotes and quotes[-1] == fragment:
                    quotes.pop()
                else:
                    quotes.append(fragment)
            if not quotes and fragment.endswith(";"):
                self.commands.append(" ".join(command))
                command = []

def initialize_database(arguments):
    import data

    dbparams = {
        "dbname": arguments.database_name,
        "user": arguments.database_username
    }

    if arguments.database_host:
        dbparams.update({
            "host": arguments.database_host,
            "port": arguments.database_port,
        })

    if arguments.database_password:
        dbparams["password"] = arguments.database_password

    db = psycopg2.connect(**dbparams)
    cursor = db.cursor()

    for script_filename in SCHEMA_FILES:
        script = SQLScript(data.load(script_filename))
        for command in script.commands:
            logger.debug(command)
            cursor.execute(command)

    cursor.execute(
        """INSERT
             INTO systemidentities (key, name, anonymous_scheme,
                                    authenticated_scheme, hostname,
                                    description, installed_sha1)
           VALUES (%s, %s, 'http', 'http', %s, 'N/A', 'N/A')""",
        (arguments.identity, arguments.identity, arguments.system_hostname))

    systemsettings = data.load_json("systemsettings.json")

    settings = systemsettings["settings"]
    privileged = set(systemsettings["privileged"])

    settings["system.hostname"] = arguments.system_hostname
    settings["paths.home"] = arguments.home_dir
    settings["paths.runtime"] = arguments.runtime_dir
    settings["paths.logs"] = arguments.logs_dir
    settings["paths.cache"] = arguments.cache_dir
    settings["paths.repositories"] = arguments.repositories_dir
    settings["paths.executables"] = os.path.dirname(sys.argv[0])

    cursor.executemany(
        """INSERT
             INTO systemsettings (identity, key, value, privileged)
           VALUES (%s, %s, %s, %s)""",
        [(arguments.identity, key, json.dumps(value), key in privileged)
         for key, value in settings.items()])

    preferences = data.load_json("preferences.json")

    for preference_name, preference_data in sorted(preferences.items()):
        relevance = preference_data.get("relevance", {})
        is_string = preference_data["type"] == "string"
        cursor.execute(
            """INSERT
                 INTO preferences (item, type, description, per_system,
                                   per_user, per_repository, per_filter)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (preference_name, preference_data["type"],
             preference_data["description"], relevance.get("system", True),
             relevance.get("user", True), relevance.get("repository", False),
             relevance.get("filter", False)))
        cursor.execute(
            """INSERT
                 INTO userpreferences (item, integer, string)
               VALUES (%s, %s, %s)""",
            (preference_name,
             int(preference_data["default"]) if not is_string else None,
             preference_data["default"] if is_string else None))

    db.commit()
    db.close()

def setup(critic, parser):
    hostname = get_hostname()

    dependencies_group = parser.add_argument_group("Dependencies")
    dependencies_group.add_argument(
        "--install-postgresql", action="store_true",
        help="Install PostgreSQL client and server packages as required.")

    system_group = parser.add_argument_group("System details")
    system_group.add_argument(
        "--identity", default="main",
        help="System identity to install.")
    system_group.add_argument(
        "--system-username", default="critic",
        help="System user to run Critic as.")
    system_group.add_argument(
        "--system-groupname", default="critic",
        help="System group to run Critic as.")
    system_group.add_argument(
        "--system-hostname", default=hostname, required=hostname is None,
        help="Fully qualified system hostname.")

    paths_group = parser.add_argument_group("Filesystem locations")
    paths_group.add_argument(
        "--home-dir", default=get_home_dir(),
        help="Main directory where persistent files are installed.")
    paths_group.add_argument(
        "--runtime-dir", default=get_runtime_dir(),
        help=("Directory in which runtime files (PID files and UNIX sockets) "
              "are created."))
    paths_group.add_argument(
        "--logs-dir", default=get_logs_dir(),
        help="Directory in which log files are created.")
    paths_group.add_argument(
        "--cache-dir", default=get_cache_dir(),
        help="Directory in which cache files are stored.")
    paths_group.add_argument(
        "--repositories-dir", default=get_repositories_dir(),
        help="Directory in which Git repositories are created.")

    database_group = parser.add_argument_group(
        "Database settings",
        description=("By default, Critic sets up a database in a PostgreSQL "
                     "running on the local machine. By specifying a database "
                     "server hostname, the system can be configured to use a "
                     "database server running on a different machine instead. "
                     "In that case, the database needs to have been created "
                     "already; this script can not do that."))
    database_group.add_argument(
        "--database-host",
        help="Optional remote host running the database server.")
    database_group.add_argument(
        "--database-port", default=5432, type=int,
        help="Database server TCP port")
    database_group.add_argument(
        "--database-name", default="critic",
        help="Name of database to connect to.")
    database_group.add_argument(
        "--database-username", default="critic",
        help="Name of database user to connect as.")
    database_group.add_argument(
        "--database-password",
        help="Database password.")
    database_group.add_argument(
        "--no-create-database", action="store_true",
        help="Assume that the named database exists already.")
    database_group.add_argument(
        "--recreate-database", action="store_true",
        help="Drop the named database first if it exists already.")
    database_group.add_argument(
        "--no-create-database-user", action="store_true",
        help=("Assume that the named database user exists already and has the "
              "required access to the named database."))

    parser.set_defaults(
        settings_dir=get_settings_dir(),
        run_as_root=True)

def main(arguments):
    from . import fail, as_user, install

    global PSQL_EXECUTABLE

    PSQL_EXECUTABLE = distutils.spawn.find_executable("psql")
    if not PSQL_EXECUTABLE:
        if not arguments.install_postgresql:
            fail("Could not find `psql` executable in $PATH!",
                 "Rerun with --install-postgresql to attempt to install "
                 "required packages automatically, or otherwise make sure it "
                 "is available and rerun this command.")
        install("postgresql-client")
        PSQL_EXECUTABLE = distutils.spawn.find_executable("psql")
        if not PSQL_EXECUTABLE:
            fail("Still could not find `psql` executable in $PATH!")

    try:
        psql("SELECT 1", arguments=arguments)
    except subprocess.CalledProcessError:
        if arguments.database_host:
            fail("Could not connect to PostgreSQL database at %s:%d!"
                 % (arguments.database_host, arguments.database_port),
                 "Please ensure that it is running and that the connection "
                 "details provided are correct.")
        if not arguments.install_postgresql:
            fail("Could not connect to local PostgreSQL database!",
                 "Rerun with --install-postgresql to attempt to install "
                 "required packages automatically, or otherwise make sure it "
                 "is available and rerun this command.")
        install("postgresql")
        try:
            psql("SELECT 1", arguments=arguments)
        except subprocess.CalledProcessError:
            fail("Still could not connect!")

    try:
        system_gid = grp.getgrnam(arguments.system_groupname).gr_gid
    except KeyError:
        logger.info("Creating system group: %s", arguments.system_groupname)
        subprocess.check_output(
            ["addgroup", "--quiet", "--system", arguments.system_groupname])
        system_gid = grp.getgrnam(arguments.system_groupname).gr_gid

    try:
        system_uid = pwd.getpwnam(arguments.system_username).pw_uid
    except KeyError:
        logger.info("Creating system user: %s", arguments.system_username)
        subprocess.check_output(
            ["adduser", "--quiet", "--system", "--disabled-login",
             "--ingroup=%s" % arguments.system_groupname,
             "--home=%s" % arguments.home_dir, arguments.system_username])
        system_uid = pwd.getpwnam(arguments.system_username).pw_uid

    database_parameters = {
        "dbname": arguments.database_name,
        "user": arguments.database_username
    }

    if arguments.database_password:
        database_parameters["password"] = arguments.database_password

    if arguments.database_host:
        database_parameters.update({
            "host": arguments.database_host,
            "port": arguments.database_port,
        })
    else:
        if arguments.system_username != arguments.database_username:
            if not arguments.database_password:
                logger.warning(
                    "System username and database username differ; a database "
                    "password is probably required for authentication to work.")

        if not arguments.no_create_database:
            try:
                psql("SELECT 1", database=arguments.database_name)
            except subprocess.CalledProcessError:
                pass
            else:
                if arguments.recreate_database:
                    psql(f'DROP DATABASE "{arguments.database_name}"')
                else:
                    fail("The database %r already exists!"
                         % arguments.database_name)

            psql(f'CREATE DATABASE "{arguments.database_name}"')
            psql(f'CREATE EXTENSION IF NOT EXISTS "plpgsql"',
                 database=arguments.database_name)

        try:
            psql("SELECT 1", database=arguments.database_name)
        except subprocess.CalledProcessError:
            fail("Failed to connect to database %r!" % arguments.database_name)

        if not arguments.no_create_database_user:
            if arguments.database_username in psql_list_roles(arguments):
                fail("The database user %r already exists!"
                     % arguments.database_username)

            create_role = (f'CREATE USER "{arguments.database_username}" '
                            'WITH LOGIN')
            if arguments.database_password:
                create_role += f" PASSWORD '{arguments.database_password}'"
            psql(create_role)

            psql(f'GRANT ALL ON DATABASE "{arguments.database_name}" '
                 f'TO "{arguments.database_username}"')

        try:
            psql("SELECT 1", database=arguments.database_name,
                 username=arguments.database_username)
        except subprocess.CalledProcessError:
            fail("Failed to connect to database %r as user %r!",
                 arguments.database_name, arguments.database_username)

    with as_user(uid=system_uid):
        initialize_database(arguments)

    ensure_dir(arguments.home_dir, uid=system_uid, gid=system_gid)
    ensure_dir(arguments.settings_dir, uid=system_uid, gid=system_gid)
    ensure_dir(arguments.runtime_dir, uid=system_uid, gid=system_gid)
    ensure_dir(arguments.logs_dir, uid=system_uid, gid=system_gid)
    ensure_dir(arguments.cache_dir, uid=system_uid, gid=system_gid)
    ensure_dir(arguments.repositories_dir, uid=system_uid, gid=system_gid)

    configuration_json = os.path.join(
        arguments.settings_dir, "configuration.json")

    with open(configuration_json, "w", encoding="utf-8") as file:
        json.dump({
            "system.identity": arguments.identity,
            "system.username": arguments.system_username,
            "system.groupname": arguments.system_groupname,
            "database.driver": "postgresql",
            "database.parameters": {
                "args": [],
                "kwargs": database_parameters,
            }
        }, file)

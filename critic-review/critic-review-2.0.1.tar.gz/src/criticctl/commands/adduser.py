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

import logging
import os
import passlib.pwd
import subprocess
import sys

logger = logging.getLogger(__name__)

import auth
import dbutils

name = "adduser"
description = "Critic administration interface: Add user"

def setup(parser):
    parser.add_argument(
        "--username", required=True,
        help="User name. Must be unique on the system.")
    parser.add_argument(
        "--fullname",
        help="Display name. Defaults to username if not specified.")
    parser.add_argument(
        "--email",
        help="Primary email address, to which Critic sends emails.")
    parser.add_argument(
        "--password",
        help=("Initial password. Defaults to a generated one, printed by this "
              "command."))
    parser.add_argument(
        "--no-password", action="store_true",
        help="Skip setting a password. The user will not be able to sign in.")
    parser.add_argument(
        "--role", action="append",
        choices=("administrator", "repositories", "developer", "newswriter"),
        help=("System role. One of: administrator, repositories, developer, "
              "and newswriter."))

    parser.set_defaults(need_session=True)

def main(critic, arguments):
    password = None
    password_generated = False

    if not arguments.no_password:
        if arguments.password:
            password = arguments.password
        else:
            password = passlib.pwd.genword()
            password_generated = True

    fullname = None
    if arguments.fullname:
        fullname = arguments.fullname.strip()
    if not fullname:
        fullname = arguments.username.strip()

    email = None
    if arguments.email:
        email = arguments.email.strip()
    if not email:
        email = None

    with critic.database.updating_cursor(
            "users", "useremails", "usergitemails", "userroles") as cursor:
        user = dbutils.User.create(
            critic.database,
            name=arguments.username.strip(),
            fullname=fullname,
            email=email,
            email_verified=None,
            password=auth.hashPassword(password))

        for role in arguments.role:
            cursor.execute(
                """INSERT
                     INTO userroles (uid, role)
                   VALUES (%s, %s)""",
                (user.id, role))

    logger.info("Created user %s [id=%d]", arguments.username.strip(), user.id)

    if password_generated:
        logger.info("Generated password: %s", password)

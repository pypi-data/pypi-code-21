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
import mimetypes
import os
import pwd
import subprocess
import tempfile

logger = logging.getLogger(__name__)

BASIC_SETTINGS = """

master = true

"""

HTTP_SOCKET = """

shared-socket = :80
http = =0

"""

HTTPS_SOCKET = """

shared-socket = :443
https = =1,%(ssl_certificate)s,%(ssl_certificate_key)s,%(ssl_ciphers)s

"""

UWSGI_BACKEND = """

# Redirect to the Critic backend.
http-to = %(sockets_dir)s/uwsgi.unix

"""

RUN_AS = """

# Run as the "web server" user/group.
uid = %(username)s
gid = %(groupname)s

"""

TEMPLATE_HTTP = """

[uwsgi]
%(basic_settings)s

%(http_socket)s

%(backend)s

%(run_as)s

"""

TEMPLATE_HTTPS = """

[uwsgi]
%(basic_settings)s

shared-socket = :80
http-to-https = =0

%(https_socket)s

%(backend)s

%(run_as)s

"""

TEMPLATE_BOTH = """

[uwsgi]
%(basic_settings)s

%(http_socket)s

%(https_socket)s

%(backend)s

%(run_as)s

"""

name = "frontend:uwsgi"
description = "Configure uWSGI as HTTP(S) front-end."

def setup(critic, parser):
    import base

    identity = base.configuration()["system.identity"]

    deps_group = parser.add_argument_group("Dependencies")
    deps_group.add_argument(
        "--install-uwsgi", action="store_true",
        help="Install uWSGI on the system if it is missing.")

    basic_group = parser.add_argument_group("Basic settings")
    basic_group.add_argument(
        "--access-scheme", choices=["http", "https", "both"], required=True,
        help="Access schemes to configure.")
    basic_group.add_argument(
        "--user", default="www-data",
        help="User to run front-end processes as.")
    basic_group.add_argument(
        "--group", default="www-data",
        help="Group to run front-end processes as.")
    basic_group.add_argument(
        "--enable-app", action="store_true",
        help="Enable the Critic front-end app.")
    basic_group.add_argument(
        "--app-file",
        default="/etc/uwsgi/apps-available/critic-frontend-%s.ini" % identity,
        help="Target path for app file")
    basic_group.add_argument(
        "--enabled-app-link",
        default="/etc/uwsgi/apps-enabled/critic-frontend-%s.ini" % identity,
        help="Target path for symlink to app file that enables the app")

    ssl_group = parser.add_argument_group("SSL settings")
    ssl_group.add_argument(
        "--ssl-certificate",
        help="Path to SSL certificate chain file.")
    ssl_group.add_argument(
        "--ssl-certificate-key",
        help="Path to SSL certificate private key file.")
    ssl_group.add_argument(
        "--ssl-ciphers",
        default="EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH",
        help=("Supported SSL ciphers. The default is strict and recommended "
              "for security rather than maximum compatibility. If the latter "
              "is important, a more relaxed setting should be used."))

    parser.set_defaults(need_session=True)

def check_uwsgi_python36(uwsgi_executable):
    try:
        process = subprocess.Popen(
            [uwsgi_executable, "--need-plugin", "python36", "--print",
             "uwsgi_python36"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        stdout, _ = process.communicate()
        return stdout == b"uwsgi_python36\n"
    except OSError:
        return False

def main(critic, arguments):
    import api

    from . import fail, as_root, install, service

    uwsgi_executable = distutils.spawn.find_executable("uwsgi")
    if not uwsgi_executable:
        if not arguments.install_uwsgi:
            fail("Could not find `uwsgi` executable in $PATH!",
                 "Rerun with --install-uwsgi to attempt to install required "
                 "packages automatically.")
        install("uwsgi")
        uwsgi_executable = distutils.spawn.find_executable("uwsgi")
        if not uwsgi_executable:
            fail("Still could not find `uwsgi` executable in $PATH!")

    if critic.settings.frontend.wsgi_container is None:
        fail("No WSGI container configured. This must be done before a front-"
             "end can be configured with the WSGI container as back-end.")
    if critic.settings.frontend.wsgi_container != "uwsgi":
        fail("Only uWSGI is currently supported as WSGI container together "
             "with an uWSGI front-end.")

    if os.path.exists(arguments.app_file):
        fail("%s: file already exists!" % arguments.app_file)
    directory = os.path.dirname(arguments.app_file)
    if not os.path.isdir(directory):
        fail("%s: no such directory!" % directory)
    if arguments.enable_app:
        if os.path.exists(arguments.enabled_app_link):
            fail("%s: file already exists!" % arguments.enabled_app_link)
        directory = os.path.dirname(arguments.enabled_app_link)
        if not os.path.isdir(directory):
            fail("%s: no such directory!" % directory)

    try:
        pwd.getpwnam(arguments.user)
    except KeyError:
        fail("%s: no such user!" % arguments.user)
    try:
        grp.getgrnam(arguments.group)
    except KeyError:
        fail("%s: no such group!" % arguments.group)

    parameters = {
        "sockets_dir": os.path.join(critic.settings.paths.runtime, "sockets"),
        "basic_settings": BASIC_SETTINGS.strip(),
        "http_socket": HTTP_SOCKET.strip(),
    }

    if arguments.access_scheme in ("https", "both"):
        if not arguments.ssl_certificate or not arguments.ssl_certificate_key:
            fail("Must specify --ssl-certificate and --ssl-certificate-key "
                 "when configuring HTTPS access. Use --access-scheme=http to "
                 "configure HTTP only, or dummy values if you want to fix the "
                 "certificate configuration manually later.")

        parameters["https_socket"] = (HTTPS_SOCKET % {
            "ssl_certificate": arguments.ssl_certificate,
            "ssl_certificate_key": arguments.ssl_certificate_key,
            "ssl_ciphers": arguments.ssl_ciphers,
        }).strip()

    parameters["backend"] = (UWSGI_BACKEND % {
        "sockets_dir": os.path.join(critic.settings.paths.runtime, "sockets"),
    }).strip()

    parameters["run_as"] = (RUN_AS % {
        "username": arguments.user,
        "groupname": arguments.group,
    }).strip()

    if arguments.access_scheme == "http":
        template = TEMPLATE_HTTP
    elif arguments.access_scheme == "https":
        template = TEMPLATE_HTTPS
    else:
        template = TEMPLATE_BOTH

    app_file_source = (template % parameters).strip()

    with as_root():
        fd, path = tempfile.mkstemp(dir=os.path.dirname(os.path.dirname(
            arguments.app_file)))

        with os.fdopen(fd, "w", encoding="utf-8") as app_file:
            print(app_file_source, file=app_file)

        os.rename(path, arguments.app_file)
        os.chmod(arguments.app_file, 0o644)

        logger.info("Created app file: %s", arguments.app_file)

        if arguments.enable_app:
            os.symlink(arguments.app_file, arguments.enabled_app_link)
            logger.info("Enabled app: %s -> %s", arguments.enabled_app_link,
                        arguments.app_file)

    if arguments.enable_app:
        service("restart", "uwsgi")

    http_frontend = api.systemsetting.fetch(critic, "frontend.http_frontend")
    access_scheme = api.systemsetting.fetch(critic, "frontend.access_scheme")

    with api.transaction.Transaction(critic) as transaction:
        transaction.setSystemSetting(http_frontend, "uwsgi")
        transaction.setSystemSetting(access_scheme, arguments.access_scheme)

    logger.info("Updated Critic's system settings:")
    logger.info("  frontend.http_frontend=%s", json.dumps("uwsgi"))
    logger.info("  frontend.access_scheme=%s",
                json.dumps(arguments.access_scheme))

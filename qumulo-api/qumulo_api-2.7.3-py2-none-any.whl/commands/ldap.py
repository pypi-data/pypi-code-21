# Copyright (c) 2017 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import qumulo.lib.auth
import qumulo.lib.opts
import qumulo.rest.ldap as ldap

LDAP_SCHEMA_OPTIONS = {"RFC2307"}

class ConfigureLdapPostCommand(qumulo.lib.opts.Subcommand):
    NAME = "ldap_set_settings"
    DESCRIPTION = "Set LDAP server settings on disk"

    @staticmethod
    def options(parser):
        parser.add_argument("--bind-uri", type=str, required=True,
            help="LDAP URI used to bind. Example: "
                "ldap://ldap-server.example.com")
        parser.add_argument("--base-dn", type=str, required=True,
            help="Base DN (Distinguished Name). Example: "
            "dc=account,dc=example,dc=com")

        # Optional arguments.
        parser.add_argument("--ldap-schema", type=str,
            choices=LDAP_SCHEMA_OPTIONS, default='RFC2307',
            help="The LDAP schema that the LDAP server uses. "
                "Default is RFC2307.")
        parser.add_argument("--bind-username", type=str, required=False,
            default='', help="Binding users's DN. Default is empty.")
        parser.add_argument("--bind-password", type=str, required=False,
            default=None, help="Password for simple authentication against "
            "LDAP server. If not specified, will use password that is "
            "currently stored on disk.")
        parser.add_argument("--gids-extension", type=str, default="enabled",
            choices={"enabled", "disabled"},
            help="Enable or disable this ldap server for extending "
            "group membership for incoming NFS request. Default is enabled.")
        parser.add_argument("--encrypt-connection", type=str,
            default="true", choices={"true", "false"},
            help="If true, LDAP conenction must be encrypted using TLS. "
            "Default is true.")

    @staticmethod
    def main(conninfo, credentials, args):
        print ldap.settings_set(conninfo, credentials,
            args.bind_uri,
            args.base_dn,
            args.ldap_schema,
            user=args.bind_username,
            password=args.bind_password,
            gids_extension=qumulo.lib.util.bool_from_string(
                args.gids_extension),
            encrypt_connection=qumulo.lib.util.bool_from_string(
                args.encrypt_connection))

class ConfigureLdapGetCommand(qumulo.lib.opts.Subcommand):
    NAME = "ldap_get_settings"
    DESCRIPTION = "Get LDAP server settings from disk"

    @staticmethod
    def main(conninfo, credentials, _args):
        print ldap.settings_get(conninfo, credentials)

class ConfigureLdapPatchCommand(qumulo.lib.opts.Subcommand):
    NAME = "ldap_update_settings"
    DESCRIPTION = "Update LDAP server settings on disk"

    @staticmethod
    def options(parser):
        parser.add_argument("--bind-uri", type=str, default=None,
            help="LDAP URI used to bind. Example: "
                "ldap://ldap-server.example.com")
        parser.add_argument("--base-dn", type=str, default=None,
            help="Base DN (Distinguished Name). Example: "
            "dc=account,dc=example,dc=com")
        parser.add_argument("--ldap-schema", type=str, default=None,
            choices=LDAP_SCHEMA_OPTIONS,
            help="The LDAP schema that the LDAP server uses.")
        parser.add_argument("--bind-username", type=str, default=None,
            help="Binding users's DN.")
        parser.add_argument("--bind-password", type=str, default=None,
            help="Password for simple authentication against "
            "LDAP server.")
        parser.add_argument("--gids-extension", type=str, default=None,
            choices={"enabled", "disabled"},
            help="Enable or disable this ldap server for extending "
            "group membership for incoming NFS request.")
        parser.add_argument("--encrypt-connection", type=str,
            default=None, choices={"true", "false"},
            help="If true, LDAP conenction must be encrypted using TLS.")

    @staticmethod
    def main(conninfo, credentials, args):
        print ldap.settings_update(conninfo, credentials,
            bind_uri=args.bind_uri,
            base_dn=args.base_dn,
            ldap_schema=args.ldap_schema,
            user=args.bind_username,
            password=args.bind_password,
            gids_extension= \
                qumulo.lib.util.bool_from_string(args.gids_extension) \
                if args.gids_extension is not None else None,
            encrypt_connection=qumulo.lib.util.bool_from_string(
                args.encrypt_connection) \
                if args.encrypt_connection is not None else None)

class UidNumberToUidGetCommand(qumulo.lib.opts.Subcommand):
    NAME = "ldap_uid_number_to_uid"
    DESCRIPTION = "Get uid from uidNumber using LDAP server"

    @staticmethod
    def options(parser):
        parser.add_argument(
            "--uid-number", type=str, required=True,
            help="Get UID (username) that corresponds to this UID number using "
            "configured LDAP server")

    @staticmethod
    def main(conninfo, credentials, args):
        print ldap.uid_number_to_uid_get(conninfo, credentials,
            args.uid_number)

class UidToGidNumbersGetCommand(qumulo.lib.opts.Subcommand):
    NAME = "ldap_uid_to_gid_numbers"
    DESCRIPTION = "Get gidNumbers the uid belongs to using LDAP server"

    @staticmethod
    def options(parser):
        parser.add_argument("--uid", type=str, required=True,
            help="Get GidNumbers that the UID (username) belongs to using "
            "configured LDAP server")

    @staticmethod
    def main(conninfo, credentials, args):
        print ldap.uid_to_gid_numbers_get(conninfo, credentials, args.uid)

class UidToUidNumberGetCommand(qumulo.lib.opts.Subcommand):
    NAME = "ldap_uid_to_uid_number"
    DESCRIPTION = "Get uidNumber from uid using LDAP server"

    @staticmethod
    def options(parser):
        parser.add_argument("--uid", type=str, required=True,
            help="Get uidNumber from uid using LDAP server")

    @staticmethod
    def main(conninfo, credentials, args):
        print ldap.uid_to_uid_number_get(conninfo, credentials, args.uid)

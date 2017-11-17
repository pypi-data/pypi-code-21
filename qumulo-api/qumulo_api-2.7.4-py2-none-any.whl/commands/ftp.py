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

import qumulo.lib.opts
import qumulo.lib.util as util
import qumulo.rest.ftp as ftp

class FtpGetStatus(qumulo.lib.opts.Subcommand):
    NAME = "ftp_get_status"
    DESCRIPTION = "Get FTP server settings and status"

    @staticmethod
    def main(conninfo, credentials, _args):
        print ftp.get_status(conninfo, credentials)

class FtpModifySettings(qumulo.lib.opts.Subcommand):
    NAME = "ftp_modify_settings"
    DESCRIPTION = "Set FTP server settings"

    @staticmethod
    def options(parser):
        parser.add_argument(
            '--enabled',
            type=util.bool_from_string,
            metavar='{true,false}',
            required=False)

        parser.add_argument(
            '--disable-host-check',
            type=util.bool_from_string,
            metavar='{true,false}',
            required=False)

    @staticmethod
    def main(conninfo, credentials, args):
        if args.enabled is None and args.disable_host_check is None:
            raise ValueError("must provide at least one argument")

        print ftp.modify_settings(
            conninfo,
            credentials,
            enabled=args.enabled,
            disable_host_check=args.disable_host_check)

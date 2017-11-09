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

import datetime

import qumulo.lib.auth
import qumulo.lib.opts
import qumulo.rest.fs as fs
import qumulo.rest.replication as replication

class ReplicationReplicate(qumulo.lib.opts.Subcommand):
    NAME = "replication_replicate"
    DESCRIPTION = "Replicate from the source to the target of the " \
        "specified relationship."

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the replication relationship")

    @staticmethod
    def main(conninfo, credentials, args):
        print replication.replicate(conninfo, credentials, args.id)

class ReplicationCreateSourceRelationship(qumulo.lib.opts.Subcommand):
    NAME = "replication_create_source_relationship"
    DESCRIPTION = "Create a new replication relationship."

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--source-id", type=str, help="File ID of the " \
            "source directory that we replicate from")
        group.add_argument("--source-path", type=str, help="Path to the " \
            "source directory that we replicate from")

        parser.add_argument(
            "--target-path", required=True,
            help="Path to the target directory that we replicate to")
        parser.add_argument(
            "--target-address", required=True,
            help="The target IP address")
        parser.add_argument(
            "--target-port", type=int, required=False,
            help="Network port to replicate to on the target "
                "(overriding default)")
        parser.add_argument(
            "--disable-continuous-replication", action="store_true",
            required=False, help="Disable continuous replication")

    @staticmethod
    def main(conninfo, credentials, args):
        optional_args = {}
        if args.target_port:
            optional_args['target_port'] = args.target_port

        if args.disable_continuous_replication:
            optional_args['disable_continuous_replication'] = True

        source_id = args.source_id if args.source_id else fs.get_file_attr(
            conninfo, credentials, path=args.source_path)[0]['id']

        print replication.create_source_relationship(
            conninfo,
            credentials,
            source_id,
            args.target_path,
            args.target_address,
            **optional_args)

class ReplicationListSourceRelationships(qumulo.lib.opts.Subcommand):
    NAME = "replication_list_source_relationships"
    DESCRIPTION = "List existing source replication relationships."

    @staticmethod
    def main(conninfo, credentials, _args):
        print replication.list_source_relationships(conninfo, credentials)

class ReplicationGetSourceRelationship(qumulo.lib.opts.Subcommand):
    NAME = "replication_get_source_relationship"
    DESCRIPTION = "Get information about the specified " \
        "source replication relationship."

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the replication relationship")

    @staticmethod
    def main(conninfo, credentials, args):
        print replication.get_source_relationship(
            conninfo, credentials, args.id)

class ReplicationDeleteSourceRelationship(qumulo.lib.opts.Subcommand):
    NAME = "replication_delete_source_relationship"
    DESCRIPTION = "Delete the specified source replication relationship."

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the replication relationship")

    @staticmethod
    def main(conninfo, credentials, args):
        replication.delete_source_relationship(conninfo, credentials, args.id)

class ReplicationModifySourceRelationship(qumulo.lib.opts.Subcommand):
    NAME = "replication_modify_source_relationship"
    DESCRIPTION = "Modify an existing source replication relationship."

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the replication relationship")

        parser.add_argument(
            "--new-target-address", required=False,
            help="The target IP address")
        parser.add_argument(
            "--new-target-port", type=int, required=False,
            help="Network port to replicate to on the target")
        parser.add_argument('-z', '--timezone', type=str,
            help='The timezone for the relationship\'s blackout windows ' \
                '(e.g. America/Los_Angeles or UTC). See the ' \
                'time_list_timezones qq command for a complete list of ' \
                'supported timezones.')

        group = parser.add_mutually_exclusive_group(required=False)
        group.add_argument("--enable-continuous-replication",
            action="store_true", help="Enable continuous replication.")
        group.add_argument("--disable-continuous-replication",
            action="store_true", help="Disable continuous replication.")

    @staticmethod
    def main(conninfo, credentials, args):
        optional_args = {}
        if args.new_target_address:
            optional_args['new_target_address'] = args.new_target_address
        if args.new_target_port:
            optional_args['new_target_port'] = args.new_target_port
        if args.timezone:
            optional_args['blackout_window_timezone'] = args.timezone
        if args.enable_continuous_replication:
            optional_args['continuous_replication_enabled'] = True
        elif args.disable_continuous_replication:
            optional_args['continuous_replication_enabled'] = False

        replication.modify_source_relationship(
            conninfo, credentials, args.id, **optional_args)

class ReplicationDeleteTargetRelationship(qumulo.lib.opts.Subcommand):
    NAME = "replication_delete_target_relationship"
    DESCRIPTION = "Delete the specified target replication relationship."

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the replication relationship")

    @staticmethod
    def main(conninfo, credentials, args):
        replication.delete_target_relationship(conninfo, credentials, args.id)

class ReplicationListSourceRelationshipStatuses(qumulo.lib.opts.Subcommand):
    NAME = "replication_list_source_relationship_statuses"
    DESCRIPTION = "List statuses for all existing source replication " \
        "relationships."

    @staticmethod
    def main(conninfo, credentials, _args):
        print replication.list_source_relationship_statuses(
            conninfo, credentials)

class ReplicationListTargetRelationshipStatuses(qumulo.lib.opts.Subcommand):
    NAME = "replication_list_target_relationship_statuses"
    DESCRIPTION = "List statuses for all existing target " \
        "replication relationships."

    @staticmethod
    def main(conninfo, credentials, _args):
        print replication.list_target_relationship_statuses(
            conninfo, credentials)

class ReplicationGetSourceRelationshipStatus(qumulo.lib.opts.Subcommand):
    NAME = "replication_get_source_relationship_status"
    DESCRIPTION = "Get current status of the specified " \
        "source replication relationship."

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the replication relationship")

    @staticmethod
    def main(conninfo, credentials, args):
        print replication.get_source_relationship_status(
            conninfo,
            credentials,
            args.id)

class ReplicationGetTargetRelationshipStatus(qumulo.lib.opts.Subcommand):
    NAME = "replication_get_target_relationship_status"
    DESCRIPTION = "Get current target of the specified " \
        "source replication relationship."

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the replication relationship")

    @staticmethod
    def main(conninfo, credentials, args):
        print replication.get_target_relationship_status(
            conninfo,
            credentials,
            args.id)

class ReplicationAuthorize(qumulo.lib.opts.Subcommand):
    NAME = "replication_authorize"
    DESCRIPTION = "Authorize the specified replication relationship, "+ \
        "establishing this cluster as the target of replication."

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the replication relationship")

    @staticmethod
    def main(conninfo, credentials, args):
        print replication.authorize(conninfo, credentials, args.id)


class ReplicationAbortReplication(qumulo.lib.opts.Subcommand):
    NAME = "replication_abort_replication"
    DESCRIPTION = "Abort ongoing replication work for the specified " \
        "source replication relationship."

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the replication relationship")

    @staticmethod
    def main(conninfo, credentials, args):
        replication.abort_replication(conninfo, credentials, args.id)

ALLOWED_DAYS = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT", "ALL"]

def get_on_days(days_of_week):
    days = [day.strip().upper() for day in days_of_week.split(",")]

    if "ALL" in days:
        if len(days) > 1:
            raise ValueError(
                "ALL cannot be used in conjunction with other days")

        # API parlance for "ALL"
        return ["EVERY_DAY"]

    if not set(days).issubset(set(ALLOWED_DAYS)):
        raise ValueError(
            "Invalid days: {}; allowed days are: {}".format(days, ALLOWED_DAYS))

    return days

def get_blackout_window(args):
    try:
        start_time = datetime.datetime.strptime(args.start_time, "%H:%M")
        end_time = datetime.datetime.strptime(args.end_time, "%H:%M")
    except ValueError:
        raise ValueError("Bad format for start/end time")

    return {
        "start_hour" : start_time.hour,
        "start_minute" : start_time.minute,
        "end_hour" : end_time.hour,
        "end_minute" : end_time.minute,
        "on_days" : get_on_days(args.days_of_week),
    }

class ReplicationAddBlackoutWindow(qumulo.lib.opts.Subcommand):
    NAME = "replication_add_blackout_window"
    DESCRIPTION = "Add a blackout window to the specified source replication " \
        "relationship."

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the replication relationship.")

        parser.add_argument("--start-time", required=True, type=str,
            help="The 24 hour time of day start time for the blackout " \
                "window (e.g 15:30).")

        parser.add_argument("--end-time", required=True, type=str,
            help="The 24 hour time of day end time for the blackout " \
                "window (e.g 18:30) -- on the following day if earlier than " \
                "the --start-time parameter.")

        parser.add_argument("--days-of-week", required=True, type=str,
            help="Days of the week the window applies to. Comma separated " \
                "list (e.g. MON,TUE,WED,THU,FRI,SAT,SUN,ALL).")

    @staticmethod
    def main(conninfo, credentials, args):
        relationship, etag = \
            replication.get_source_relationship(conninfo, credentials, args.id)

        blackout_windows = relationship['blackout_windows']

        blackout_windows.append(get_blackout_window(args))

        print replication.modify_source_relationship(
            conninfo,
            credentials,
            args.id,
            blackout_windows=blackout_windows,
            etag=etag)

class ReplicationDeleteBlackoutWindows(qumulo.lib.opts.Subcommand):
    NAME = "replication_delete_blackout_windows"
    DESCRIPTION = "Delete blackout windows of the specified source " \
        "replication relationship."

    @staticmethod
    def options(parser):
        parser.add_argument("--id", required=True,
            help="Unique identifier of the replication relationship")

    @staticmethod
    def main(conninfo, credentials, args):
        _, etag = \
            replication.get_source_relationship(conninfo, credentials, args.id)

        print replication.modify_source_relationship(
            conninfo, credentials, args.id, blackout_windows=[], etag=etag)

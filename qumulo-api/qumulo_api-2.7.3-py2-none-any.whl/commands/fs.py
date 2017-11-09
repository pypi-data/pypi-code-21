# Copyright (c) 2012 Qumulo, Inc.
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
import qumulo.rest.fs as fs
import qumulo.lib.request as request

import qumulo.lib.util

import os.path
import sys
import json

AGG_ORDERING_CHOICES = [
    "total_blocks",
    "total_datablocks",
    "total_metablocks",
    "total_files",
    "total_directories",
    "total_symlinks",
    "total_other"]

LOCK_RELEASE_FORCE_MSG = "Manually releasing locks may cause data corruption, "\
                         "do you want to proceed?"

def all_elements_none(iterable):
    for element in iterable:
        if element is not None:
            return False
    return True

class GetStatsCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_get_stats"
    DESCRIPTION = "Get file system statistics"

    @staticmethod
    def main(conninfo, credentials, _args):
        print fs.read_fs_stats(conninfo, credentials)

class GetFileAttrCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_file_get_attr"
    DESCRIPTION = "Get file attributes"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="Path to file", type=str)
        group.add_argument("--id", help="File ID", type=str)
        parser.add_argument("--snapshot", help="Snapshot ID to read from",
            type=int)

    @staticmethod
    def main(conninfo, credentials, args):
        print fs.get_file_attr(conninfo, credentials, id_=args.id,
            path=args.path, snapshot=args.snapshot)

class SetFileAttrCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_file_set_attr"
    DESCRIPTION = "Set file attributes"

    @staticmethod
    def options(parser):
        parser.add_argument("--id", help="File id", type=str, required=True)
        parser.add_argument("--mode", type=str,
                            help="Posix-style file mode (octal)")
        parser.add_argument("--size", help="File size", type=str)
        parser.add_argument("--creation-time", type=str,
                            help='File creation time (as RFC 3339 string)')
        parser.add_argument("--modification-time", type=str,
                            help='File modification time (as RFC 3339 string)')
        parser.add_argument("--change-time", type=str,
                            help='File change time (as RFC 3339 string)')

        owner_group = parser.add_mutually_exclusive_group()
        owner_group.add_argument("--owner",
            help="File owner as auth_id", type=str)
        owner_group.add_argument("--owner-local",
            help="File owner as local user name", type=fs.LocalUser)
        owner_group.add_argument("--owner-sid",
            help="File owner as SID", type=fs.SMBSID)
        owner_group.add_argument("--owner-uid",
            help="File owner as NFS UID", type=fs.NFSUID)

        group_group = parser.add_mutually_exclusive_group()
        group_group.add_argument("--group",
            help="File group as auth_id", type=str)
        group_group.add_argument("--group-local",
            help="File group as local group name", type=fs.LocalGroup)
        group_group.add_argument("--group-sid",
            help="File group as SID", type=fs.SMBSID)
        group_group.add_argument("--group-gid",
            help="File group as NFS GID", type=fs.NFSGID)

    @staticmethod
    def main(conninfo, credentials, args):
        owner = args.owner or \
                args.owner_local or args.owner_sid or args.owner_uid
        group = args.group or \
                args.group_local or args.group_sid or args.group_gid

        if all_elements_none([args.mode, owner, group, args.size,
                              args.creation_time, args.modification_time,
                              args.change_time]):
            raise ValueError("Must specify at least one option to change.")

        print fs.set_file_attr(conninfo, credentials,
                args.mode, owner, group, args.size,
                args.creation_time, args.modification_time, args.change_time,
                args.id)

class SetExtendedFileAttrsCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_file_set_extended_attrs"
    DESCRIPTION = "Set SMB extended attributes on the file"

    @staticmethod
    def options(parser):
        parser.add_argument("--id", help="File id", type=str, required=True)
        parser.add_argument("ARCHIVE", metavar="ARCHIVE",
                choices=['true', 'false'], help="{true, false}")
        parser.add_argument("COMPRESSED", metavar="COMPRESSED",
                choices=['true', 'false'], help="{true, false}")
        parser.add_argument("HIDDEN", metavar="HIDDEN",
                choices=['true', 'false'], help="{true, false}")
        parser.add_argument("NOT_CONTENT_INDEXED",
                metavar="NOT_CONTENT_INDEXED",
                choices=['true', 'false'], help="{true, false}")
        parser.add_argument("READ_ONLY", metavar="READ_ONLY",
                choices=['true', 'false'], help="{true, false}")
        parser.add_argument("SYSTEM", metavar="SYSTEM",
                choices=['true', 'false'], help="{true, false}")
        parser.add_argument("TEMPORARY", metavar="TEMPORARY",
                choices=['true', 'false'], help="{true, false}")

    @staticmethod
    def main(conninfo, credentials, args):
        def str_to_bool(val):
            return val == "true"

        attr_map = {
            "archive": str_to_bool(args.ARCHIVE),
            "compressed": str_to_bool(args.COMPRESSED),
            "hidden": str_to_bool(args.HIDDEN),
            "not_content_indexed": str_to_bool(args.NOT_CONTENT_INDEXED),
            "read_only": str_to_bool(args.READ_ONLY),
            "system": str_to_bool(args.SYSTEM),
            "temporary": str_to_bool(args.TEMPORARY),
        }

        print fs.set_file_attr(conninfo, credentials,
            None, None, None, None, None, None, None,
            args.id,
            extended_attrs=attr_map)

class GetAclCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_get_acl"
    DESCRIPTION = "Get file ACL"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="Path to file", type=str)
        group.add_argument("--id", help="File ID", type=str)
        parser.add_argument("--snapshot", help="Snapshot ID to read from",
            type=int)

    @staticmethod
    def main(conninfo, credentials, args):
        print fs.get_acl(conninfo, credentials, args.path, args.id,
            snapshot=args.snapshot)

class SetAclCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_set_acl"
    DESCRIPTION = "Set file ACL"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="Path to file", type=str)
        group.add_argument("--id", help="File id", type=str)
        parser.add_argument("--file", help="Local file containing ACL JSON"
                            " containing control flags and ACEs",
                            required=False, type=str)

    @staticmethod
    def main(conninfo, credentials, args):
        if not bool(args.file):
            raise ValueError('Must specify --file')

        acl_control = None
        acl_aces = None
        with open(args.file) as f:
            contents = f.read()
            try:
                acl_contents = json.loads(contents)
                acl = acl_contents.get("acl")
                acl_control = acl.get("control")
                acl_aces = acl.get("aces")
            except ValueError, e:
                raise ValueError("Error parsing ACL data: %s\n" % str(e))

        etag = None
        print fs.set_acl(conninfo, credentials, path=args.path,
                id_=args.id, control=acl_control, aces=acl_aces,
                if_match=etag)

class CreateFileCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_create_file"
    DESCRIPTION = "Create a new file"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="Path to parent directory")
        group.add_argument("--id", help="ID of parent directory")
        parser.add_argument("--name", help="New file name", required=True)

    @staticmethod
    def main(conninfo, credentials, args):
        print fs.create_file(conninfo, credentials, args.name,
            dir_path=args.path, dir_id=args.id)

class CreateDirectoryCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_create_dir"
    DESCRIPTION = "Create a new directory"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="Path to parent directory")
        group.add_argument("--id", help="ID of parent directory")
        parser.add_argument("--name", help="New directory name", required=True)

    @staticmethod
    def main(conninfo, credentials, args):
        print fs.create_directory(conninfo, credentials, args.name,
            dir_path=args.path, dir_id=args.id)

class CreateSymlinkCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_create_symlink"
    DESCRIPTION = "Create a new symbolic link"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="Path to parent directory")
        group.add_argument("--id", help="ID of parent directory")
        parser.add_argument("--target", help="Link target", required=True)
        parser.add_argument("--target-type", help="Link target type")
        parser.add_argument("--name", help="New symlink name", required=True)

    @staticmethod
    def main(conninfo, credentials, args):
        print fs.create_symlink(
            conninfo,
            credentials,
            args.name,
            args.target,
            dir_path=args.path,
            dir_id=args.id,
            target_type=args.target_type)

def parse_major_minor_numbers(major_minor_numbers):
    if major_minor_numbers is None:
        return None
    major, _, minor = major_minor_numbers.partition(',')
    return {
        'major': int(major),
        'minor': int(minor)
    }

class CreateUNIXFileCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_create_unix_file"
    DESCRIPTION = "Create a new pipe, character device, block device or socket"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="Path to parent directory")
        group.add_argument("--id", help="ID of parent directory")
        parser.add_argument(
            "--major-minor-numbers", help="Major and minor numbers")
        parser.add_argument("--name", help="New file name", required=True)
        parser.add_argument(
            "--type", help="type of UNIX file to create", required=True)

    @staticmethod
    def main(conninfo, credentials, args):
        major_minor_numbers = \
            parse_major_minor_numbers(args.major_minor_numbers)
        print fs.create_unix_file(
            conninfo,
            credentials,
            name=args.name,
            file_type=args.type,
            major_minor_numbers=major_minor_numbers,
            dir_path=args.path,
            dir_id=args.id)

class CreateLinkCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_create_link"
    DESCRIPTION = "Create a new link"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="Path to parent directory")
        group.add_argument("--id", help="ID of parent directory")
        parser.add_argument("--target", help="Link target", required=True)
        parser.add_argument("--name", help="New link name", required=True)

    @staticmethod
    def main(conninfo, credentials, args):
        print fs.create_link(conninfo, credentials, args.name,
            args.target, dir_path=args.path, dir_id=args.id)

class RenameCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_rename"
    DESCRIPTION = "Rename a file system object"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path",
            help="Path to destination parent directory")
        group.add_argument("--id", help="ID of destination parent directory")
        parser.add_argument("--source", help="Source file path", required=True)
        parser.add_argument("--name", help="New name in destination directory",
            required=True)

    @staticmethod
    def main(conninfo, credentials, args):
        print fs.rename(conninfo, credentials, args.name,
            args.source, dir_path=args.path, dir_id=args.id)

class DeleteCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_delete"
    DESCRIPTION = "Delete a file system object"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="Path to file system object")
        group.add_argument("--id", help="ID of file system object")

    @staticmethod
    def main(conninfo, credentials, args):
        fs.delete(conninfo, credentials, path=args.path, id_=args.id)
        print "File system object was deleted."

class WriteFileCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_write"
    DESCRIPTION = "Write data to a file"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="Path to file", type=str)
        group.add_argument("--id", help="File id", type=str)
        parser.add_argument("--offset", type=int,
                            help="Offset at which to write data. If not "
                                 "specified, the existing contents of the file "
                                 "will be replaced with the given contents.")
        parser.add_argument("--file", help="File data to send", type=str)
        parser.add_argument("--create", action="store_true",
                            help="Create file before writing (fails if exists)")
        parser.add_argument("--stdin", action="store_true",
                            help="Write file from stdin")

    @staticmethod
    def main(conninfo, credentials, args):
        if args.id and args.create:
            raise ValueError("cannot use --create with --id")
        if args.stdin:
            if args.file:
                raise ValueError("--stdin conflicts with --file")
            elif not args.chunked:
                raise ValueError("--stdin must be sent chunked")
        elif args.file:
            if not os.path.isfile(args.file):
                raise ValueError("%s is not a file" % args.file)
        else:
            raise ValueError("Must specify --stdin or --file")

        infile = open(args.file, "rb") if args.file else sys.stdin

        if args.create:
            dirname, basename = qumulo.lib.util.unix_path_split(args.path)
            if not basename:
                raise ValueError("Path has no basename")
            fs.create_file(conninfo, credentials, basename, dirname)

        etag = None
        print fs.write_file(conninfo, credentials, infile,
            args.path, args.id, etag, args.offset)

class ReadFileCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_read"
    DESCRIPTION = "Read a file"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="Path to file", type=str)
        group.add_argument("--id", help="File id", type=str)
        parser.add_argument("--snapshot", help="Snapshot ID to read from",
                            type=int)
        parser.add_argument("--offset", type=int,
                            help="Offset at which to read data. If not "
                                 "specified, read from the beginning of the "
                                 "file.")
        parser.add_argument("--length", type=int,
                            help="Amount of data to read. If not specified, "
                                 "read the entire file.")
        parser.add_argument("--file", help="File to receive data", type=str)
        parser.add_argument("--force", action='store_true',
                            help="Overwrite an existing file")
        parser.add_argument("--stdout", action='store_const', const=True,
                            help="Output data to standard out")

    @staticmethod
    def main(conninfo, credentials, args):
        if args.stdout:
            if args.file:
                raise ValueError("--stdout conflicts with --file")
        elif args.file:
            if os.path.exists(args.file) and not args.force:
                raise ValueError("%s already exists." % args.file)
        else:
            raise ValueError("Must specify --stdout or --file")

        if args.file is None:
            f = sys.stdout
        else:
            f = open(args.file, "wb")

        fs.read_file(conninfo, credentials, f, path=args.path,
            id_=args.id, snapshot=args.snapshot, offset=args.offset,
            length=args.length)
        # Print nothing on success (File may be output into stdout)

class ReadDirectoryCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_read_dir"
    DESCRIPTION = "Read directory"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="Directory path", type=str)
        group.add_argument("--id", help="Directory id", type=str)
        parser.add_argument("--page-size", type=int,
                            help="Max directory entries to return per request")
        parser.add_argument("--snapshot", help="Snapshot ID to read from",
                            type=int)

    @staticmethod
    def main(conninfo, credentials, args):
        if args.page_size is not None and args.page_size < 1:
            raise ValueError("Page size must be greater than 0")

        page = fs.read_directory(conninfo, credentials,
            page_size=args.page_size,
            path=args.path,
            id_=args.id,
            snapshot=args.snapshot)

        print page

        next_uri = json.loads(str(page))["paging"]["next"]
        while next_uri != "":
            page = request.rest_request(conninfo, credentials, "GET", next_uri)
            print page
            next_uri = json.loads(str(page))["paging"]["next"]

class ReadDirectoryCapacityCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_read_dir_aggregates"
    DESCRIPTION = "Read directory aggregation entries"

    @staticmethod
    def options(parser):
        parser.add_argument("--path", help="Directory path", type=str,
            required=True)
        parser.add_argument("--recursive", action="store_true",
            help="Fetch recursive aggregates")
        parser.add_argument("--max-entries",
            help="Maximum number of entries to return", type=int)
        parser.add_argument("--max-depth",
            help="Maximum depth to recurse when --recursive is set", type=int)
        parser.add_argument("--order-by", choices=AGG_ORDERING_CHOICES,
            help="Specify field used for top N selection and sorting")
        parser.add_argument("--snapshot", type=int,
            help="Snapshot ID to read from")

    @staticmethod
    def main(conninfo, credentials, args):
        print fs.read_dir_aggregates(conninfo, credentials,
            args.path, args.recursive, args.max_entries, args.max_depth,
            args.order_by, snapshot=args.snapshot)

class TreeWalkCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_walk_tree"
    DESCRIPTION = "Walk file system tree"

    @staticmethod
    def options(parser):
        parser.add_argument("--path", help="Path to tree root", type=str,
                            required=False, default='/')

    @staticmethod
    def main(conninfo, credentials, args):
        for f, _etag in fs.tree_walk_preorder(conninfo, credentials, args.path):
            print '%s sz=%s owner=%s group=%s ' \
                  'owner_id_type=%s owner_id_value=%s ' \
                  'group_id_type=%s group_id_value=%s' % (
                f['path'], f['size'], f['owner'],
                f['group'], f['owner_details']['id_type'],
                str(f['owner_details']['id_value']),
                f['group_details']['id_type'],
                str(f['group_details']['id_value']))

def ask_for_delete_tree(target):
    message = 'Are you sure you want to delete "{}" and all its descendants' \
        .format(target)
    return qumulo.lib.opts.ask("fs_delete_tree", message)

class TreeDeleteCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_delete_tree"
    DESCRIPTION = "Delete file system tree recursively"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="Path to tree root")
        group.add_argument("--id", help="ID of tree root")

    @staticmethod
    def main(conninfo, credentials, args):
        if args.path is None:
            paths, _etag = fs.resolve_paths(conninfo, credentials, [args.id])
            path = paths[0]['path']
        else:
            path = args.path

        if ask_for_delete_tree(path):
            print fs.delete_tree(
                conninfo, credentials, path=args.path, id_=args.id)
            print "Tree delete initiated."

class TreeDeleteStatusCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_delete_tree_status"
    DESCRIPTION = "Status of a tree-delete job"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="Path to tree root")
        group.add_argument("--id", help="ID of tree root")

    @staticmethod
    def main(conninfo, credentials, args):
        print fs.tree_delete_status(
            conninfo, credentials, path=args.path, id_=args.id)

class GetFileSamplesCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_file_samples"
    DESCRIPTION = "Get a number of sample files from the file system"

    @staticmethod
    def options(parser):
        parser.add_argument("--path", required=True)
        parser.add_argument("--count", type=int, required=True)
        parser.add_argument("--sample-by",
                            choices=['capacity', 'input-ops', 'file'],
                            help="Weight sampling by the given value")

    @staticmethod
    def main(conninfo, credentials, args):
        print fs.get_file_samples(conninfo, credentials, args.path, args.count,
                                  args.sample_by)

class ResolvePathsCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_resolve_paths"
    DESCRIPTION = "Resolve file IDs to paths"

    @staticmethod
    def options(parser):
        parser.add_argument("--ids", required=True, nargs="*",
            help="File IDs to resolve")
        parser.add_argument("--snapshot", help="Snapshot ID to read from",
            type=int)

    @staticmethod
    def main(conninfo, credentials, args):
        print fs.resolve_paths(conninfo, credentials, args.ids,
            snapshot=args.snapshot)

class ListLocksByFileCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_list_locks_by_file"
    DESCRIPTION = "List locks held on a particular files"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="File path", type=str)
        group.add_argument("--id", help="File id", type=str)
        parser.add_argument("--protocol", type=str, required=True,
            choices = { p for p, t in fs.VALID_LOCK_PROTO_TYPE_COMBINATIONS },
            help="The protocol whose locks should be listed")
        parser.add_argument("--lock-type", type=str, required=True,
            choices = { t for p, t in fs.VALID_LOCK_PROTO_TYPE_COMBINATIONS },
            help="The type of lock to list.")
        parser.add_argument("--snapshot", type=str,
            help="Snapshot id of the specified file.")

    @staticmethod
    def main(conninfo, credentials, args):
        if (args.protocol, args.lock_type) not in \
                fs.VALID_LOCK_PROTO_TYPE_COMBINATIONS:
            raise ValueError(
                "Lock type {} not available for protocol {}".format(
                    args.lock_type, args.protocol))

        print json.dumps(
            fs.list_all_locks_by_file(
                conninfo,
                credentials,
                args.protocol,
                args.lock_type,
                args.path,
                args.id,
                args.snapshot),
            indent=4)

class ListLocksByClientCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_list_locks_by_client"
    DESCRIPTION = "List locks held by a particular client machine"

    @staticmethod
    def options(parser):
        parser.add_argument("--protocol", type=str, required=True,
            choices = { p for p, t in fs.VALID_LOCK_PROTO_TYPE_COMBINATIONS },
            help="The protocol whose locks should be listed")
        parser.add_argument("--lock-type", type=str, required=True,
            choices = { t for p, t in fs.VALID_LOCK_PROTO_TYPE_COMBINATIONS },
            help="The type of lock to list.")
        parser.add_argument("--name", help="Client hostname", type=str)
        parser.add_argument("--address", help="Client IP address", type=str)

    @staticmethod
    def main(conninfo, credentials, args):
        if (args.protocol, args.lock_type) not in \
                fs.VALID_LOCK_PROTO_TYPE_COMBINATIONS:
            raise ValueError(
                "Lock type {} not available for protocol {}".format(
                    args.lock_type, args.protocol))

        if args.name and (args.protocol != 'nlm'):
            raise ValueError("--name may only be specified for NLM locks")

        print json.dumps(
            fs.list_all_locks_by_client(
                conninfo,
                credentials,
                args.protocol,
                args.lock_type,
                args.name,
                args.address),
            indent=4)

class ListWaitersByFileCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_list_lock_waiters_by_file"
    DESCRIPTION = "List waiting lock requests for a particular files"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="File path", type=str)
        group.add_argument("--id", help="File id", type=str)
        parser.add_argument("--protocol", type=str, required=True,
            choices = { p for p, t in fs.VALID_WAITER_PROTO_TYPE_COMBINATIONS },
            help="The protocol whose lock waiters should be listed")
        parser.add_argument("--lock-type", type=str, required=True,
            choices = { t for p, t in fs.VALID_WAITER_PROTO_TYPE_COMBINATIONS },
            help="The type of lock whose waiters should be listed")
        parser.add_argument("--snapshot", type=str,
            help="Snapshot id of the specified file.")

    @staticmethod
    def main(conninfo, credentials, args):
        if (args.protocol, args.lock_type) not in \
                fs.VALID_WAITER_PROTO_TYPE_COMBINATIONS:
            raise ValueError(
                "Lock type {} not available for protocol {}".format(
                    args.lock_type, args.protocol))

        print json.dumps(
            fs.list_all_waiters_by_file(
                conninfo,
                credentials,
                args.protocol,
                args.lock_type,
                args.path,
                args.id,
                args.snapshot),
            indent=4)

class ListWaitersByClientCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_list_lock_waiters_by_client"
    DESCRIPTION = "List waiting lock requests for a particular client machine"

    @staticmethod
    def options(parser):
        parser.add_argument("--protocol", type=str, required=True,
            choices = { p for p, t in fs.VALID_WAITER_PROTO_TYPE_COMBINATIONS },
            help="The protocol whose lock waiters should be listed")
        parser.add_argument("--lock-type", type=str, required=True,
            choices = { t for p, t in fs.VALID_WAITER_PROTO_TYPE_COMBINATIONS },
            help="The type of lock whose waiters should be listed")
        parser.add_argument("--name", help="Client hostname", type=str)
        parser.add_argument("--address", help="Client IP address", type=str)

    @staticmethod
    def main(conninfo, credentials, args):
        if (args.protocol, args.lock_type) not in \
                fs.VALID_WAITER_PROTO_TYPE_COMBINATIONS:
            raise ValueError(
                "Lock type {} not available for protocol {}".format(
                    args.lock_type, args.protocol))

        if args.name and (args.protocol != 'nlm'):
            raise ValueError("--name may only be specified for NLM locks")

        print json.dumps(
            fs.list_all_waiters_by_client(
                conninfo,
                credentials,
                args.protocol,
                args.lock_type,
                args.name,
                args.address),
            indent=4)

class ReleaseNLMLocksByClientCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_release_nlm_locks_by_client"
    DESCRIPTION = '''Release NLM byte range locks held by client. This method
    releases all locks held by a particular client. This is dangerous, and
    should only be used after confirming that the client is dead.'''

    @staticmethod
    def options(parser):
        parser.add_argument("--force",
            help="This command can cause corruption, add this flag to \
                release lock", action='store_true', required=False)
        parser.add_argument("--name", help="Client hostname", type=str)
        parser.add_argument("--address", help="Client IP address", type=str)

    @staticmethod
    def main(conninfo, credentials, args):
        if not args.name and not args.address:
            raise ValueError("Must specify --name or --address")

        if not args.force and not qumulo.lib.opts.ask(
                ReleaseNLMLocksByClientCommand.NAME, LOCK_RELEASE_FORCE_MSG):
            return # Operation cancelled.

        fs.release_nlm_locks_by_client(
                conninfo,
                credentials,
                args.name,
                args.address)
        params = ""
        if args.name:
            params += "owner_name: {}".format(args.name)
        if args.name and args.address:
            params += ", "
        if args.address:
            params += "owner_address: {}".format(args.address)
        print "NLM byte-range locks held by {} were released.".format(params)

class ReleaseNLMLockCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_release_nlm_lock"
    DESCRIPTION = '''Release an arbitrary NLM byte-range lock range. This is
    dangerous, and should only be used after confirming that the owning process
    has leaked the lock, and only if there is a very good reason why the
    situation should not be resolved by terminating that process.'''

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--path", help="File path", type=str)
        group.add_argument("--id", help="File id", type=str)
        parser.add_argument("--offset", help="NLM byte-range lock offset",
                required=True, type=str)
        parser.add_argument("--size", help="NLM byte-range lock size",
                required=True, type=str)
        parser.add_argument("--owner-id", help="Owner id",
                required=True, type=str)
        parser.add_argument("--force",
                help="This command can cause corruption, add this flag to \
                        release lock", action='store_true', required=False)
        parser.add_argument("--snapshot",
            help="Snapshot ID of the specified file", type=str)

    @staticmethod
    def main(conninfo, credentials, args):
        if not args.force and not qumulo.lib.opts.ask(
                ReleaseNLMLockCommand.NAME, LOCK_RELEASE_FORCE_MSG):
            return # Operation cancelled.

        fs.release_nlm_lock(
                conninfo,
                credentials,
                args.offset,
                args.size,
                args.owner_id,
                args.path,
                args.id,
                args.snapshot)

        file_path_or_id = ""
        if args.path is not None:
            file_path_or_id = "file_path: {}".format(args.path)
        if args.id is not None:
            file_path_or_id = "file_id: {}".format(args.id)

        snapshot = ""
        if args.snapshot is not None:
            snapshot = ", snapshot: {}".format(args.snapshot)

        output = (
            "NLM byte-range lock with "
            "(offset: {0}, size: {1}, owner-id: {2}, {3}{4})"
            " was released."
            ).format(args.offset, args.size, args.owner_id,
            file_path_or_id, snapshot)

        print output

class ModifySettingsCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_modify_settings"
    DESCRIPTION = "Modify filesystem settings"

    @staticmethod
    def options(parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "--enable-merged-permissions", action="store_true", help="Enable")
        group.add_argument(
            "--disable-merged-permissions", action="store_true", help="Disable")

    @staticmethod
    def main(conninfo, credentials, args):
        settings = {}
        if args.enable_merged_permissions:
            settings['merged_permissions'] = True
        else:
            assert args.disable_merged_permissions
            settings['merged_permissions'] = False

        print fs.modify_settings(conninfo, credentials, settings)

class GetSettingsCommand(qumulo.lib.opts.Subcommand):
    NAME = "fs_get_settings"
    DESCRIPTION = "Get the current filesystem settings"

    @staticmethod
    def main(conninfo, credentials, _args):
        print fs.get_settings(conninfo, credentials)

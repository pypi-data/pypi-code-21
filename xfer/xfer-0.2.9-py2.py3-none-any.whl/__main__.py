# -*- coding: utf-8 -*-
#
# Main entry point for xfer
# 
# @author <bprinty@gmail.com>
# ------------------------------------------------


# imports
# -------
import os
import sys
import argparse

from . import __version__
from . import cli


# args
# ----
parser = argparse.ArgumentParser()
# parser.add_argument('-o', '--option', help='Arbitrary option -- uncomment and update to use.', default=None)
subparsers = parser.add_subparsers()


# version
# -------
parser_version = subparsers.add_parser('version')
parser_version.set_defaults(func=lambda x: sys.stderr.write(__version__ + '\n'))


# config
# ------
parser_config = subparsers.add_parser('config')
parser_config.add_argument('type', nargs='?', help='Type of remote to configure.', default='ssh')
parser_config.set_defaults(func=cli.config)


# add
# ---
parser_add = subparsers.add_parser('add')
parser_add.add_argument('files', nargs='+', help='Files to add for tracking.')
parser_add.set_defaults(func=cli.add)


# list
# ----
parser_list = subparsers.add_parser('list')
parser_list.add_argument('remote', nargs='?', help='Files to add for tracking.', default='local')
parser_list.set_defaults(func=cli.list)


# prune
# -----
parser_prune = subparsers.add_parser('prune')
parser_prune.set_defaults(func=cli.prune)


# reset
# -----
parser_reset = subparsers.add_parser('reset')
parser_reset.set_defaults(func=cli.reset)


# remove
# ------
parser_remove = subparsers.add_parser('remove')
parser_remove.add_argument('-d', '--delete', action='store_true', help='Delete files from filesystem in addition to removing them from xfer tracking.', default=False)
parser_remove.add_argument('files', nargs='+', help='Files to remove from tracking.')
parser_remove.set_defaults(func=cli.remove)


# rm
# --
parser_rm = subparsers.add_parser('rm')
parser_rm.add_argument('files', nargs='+', help='Files to delete and remove from tracking.')
parser_rm.set_defaults(func=cli.rm)


# diff
# ----
parser_diff = subparsers.add_parser('diff')
parser_diff.add_argument('remote', help='Remote to compare with local repository.')
parser_diff.set_defaults(func=cli.diff)


# push
# ----
parser_push = subparsers.add_parser('push')
parser_push.add_argument('remote', help='Remote to push tracked files to.')
parser_push.set_defaults(func=cli.push)


# pull
# ----
parser_pull = subparsers.add_parser('pull')
parser_pull.add_argument('remote', help='Remote to pull tracked files from.')
parser_pull.set_defaults(func=cli.pull)


# exec
# ----
def main():
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()


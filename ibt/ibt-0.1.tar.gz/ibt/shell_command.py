###############################################################################
#
# IBT: Isolated Build Tool
# Copyright (C) 2016, Richard Cook. All rights reserved.
#
# Simple wrappers around Docker etc. for fully isolated build environments
#
###############################################################################

from __future__ import print_function
import argparse

from ibt.command import Command
from ibt.container_util import call_process_in_container
from ibt.docker_util import docker_image_exists

class ShellCommand(Command):
    def __init__(self):
        super(ShellCommand, self).__init__("shell", requires_project=True)

    def add_subparser(self, subparsers):
        p = subparsers.add_parser(self.name, help="Run interactive shell inside container")
        p.add_argument("command", metavar="COMMAND", nargs="?", help="command")
        p.add_argument("args", metavar="ARGS", nargs=argparse.REMAINDER, help="arguments")
        p.set_defaults(obj=self, handler=self.run)

    def run(self, ctx, project, args):
        if not docker_image_exists(project.image_id):
            raise RuntimeError("Project has not been upped")

        user_command = args.args if args.command is None else [args.command] + args.args
        status = call_process_in_container(ctx, project, args, ["-it"], user_command)
        if status != 0:
            print("Shell returned {}".format(status))

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
import os

from ibt.command import Command
from ibt.docker_util import docker_image_exists, docker_run
from ibt.util import make_shell_script, temp_dir

class RunCommand(Command):
    def __init__(self):
        super(RunCommand, self).__init__("run", requires_project=True)

    def add_subparser(self, subparsers):
        p = subparsers.add_parser(self.name, help="Run command inside container")
        p.add_argument("command", metavar="COMMAND", help="command")
        p.add_argument("args", metavar="ARGS", nargs=argparse.REMAINDER, help="arguments")
        p.set_defaults(obj=self, handler=self.run)

    def run(self, ctx, project, args):
        if not docker_image_exists(project.image_id):
            raise RuntimeError("Project has not been upped")

        self.run_lines(ctx, project, args, [" ".join([args.command] + args.args)])

    def run_lines(self, ctx, project, args, lines):
        with temp_dir(project.dot_dir) as dir:
            local_path = os.path.join(dir, "script")
            container_path = os.path.join(project.container_dot_dir, os.path.relpath(local_path, project.dot_dir))
            make_shell_script(local_path, lines)
            docker_run(ctx, project, args, container_path)

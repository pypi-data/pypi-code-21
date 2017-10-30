###############################################################################
#
# IBT: Isolated Build Tool
# Copyright (C) 2016, Richard Cook. All rights reserved.
#
# Simple wrappers around Docker etc. for fully isolated build environments
#
###############################################################################

from __future__ import print_function
import os
import shutil

from ibt.command import Command
from ibt.docker_util import docker_image_exists
from ibt.util import temp_dir

class ScriptCommand(Command):
    def __init__(self):
        super(ScriptCommand, self).__init__("script", requires_project=True)

    def add_subparser(self, subparsers):
        p = subparsers.add_parser(self.name, help="Run script inside container")
        p.add_argument("script_path", metavar="SCRIPTPATH", help="script to run")
        p.set_defaults(obj=self, handler=self.run)

    def run(self, ctx, project, args):
        if not docker_image_exists(project.image_id):
            raise RuntimeError("Project has not been upped")

        with temp_dir(project.dot_dir) as dir:
            local_path = os.path.join(dir, "script")
            container_path = os.path.join(project.container_dot_dir, os.path.relpath(local_path, project.dot_dir))

            local_input_path = os.path.join(dir, "input")
            container_input_path = os.path.join(project.container_dot_dir, os.path.relpath(local_input_path, project.dot_dir))

            shutil.copyfile(args.script_path, local_input_path)

            with open(local_path, "wt") as f:
                f.write("#!/bin/sh\n")
                f.write("chmod +x {}\n".format(container_input_path))
                f.write(container_input_path + "\n")

            docker_run(ctx, args, container_path)

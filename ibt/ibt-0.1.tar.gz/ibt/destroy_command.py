###############################################################################
#
# IBT: Isolated Build Tool
# Copyright (C) 2016, Richard Cook. All rights reserved.
#
# Simple wrappers around Docker etc. for fully isolated build environments
#
###############################################################################

from __future__ import print_function

from ibt.command import Command
from ibt.docker_util import docker_image_remove

class DestroyCommand(Command):
    def __init__(self):
        super(DestroyCommand, self).__init__("destroy", requires_project=True)

    def add_subparser(self, subparsers):
        p = subparsers.add_parser(self.name, help="Destroy project image")
        p.set_defaults(obj=self, handler=self.run)

    def run(self, _0, project, _1):
        docker_image_remove(project.image_id)

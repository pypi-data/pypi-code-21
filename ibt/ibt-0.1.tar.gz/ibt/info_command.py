###############################################################################
#
# IBT: Isolated Build Tool
# Copyright (C) 2017, Richard Cook. All rights reserved.
#
# Simple wrappers around Docker etc. for fully isolated build environments
#
###############################################################################

from __future__ import print_function
import os

from ibt.command import Command
from ibt.docker_util import docker_image_exists, docker_installed
from ibt.project import Project
from ibt.util import show_banner

def _show_system_info(ctx):
    uid, group_name, gid, user_name = ctx.user_info()

    print("System information:")
    print("  Docker:              {}".format("installed" if docker_installed() else "not installed"))
    print()

    print("Context information:")
    print("  Working directory:   {}".format(ctx.working_dir))
    print("  User:                {} ({})".format(user_name, uid))
    print("  Group:               {} ({})".format(group_name, gid))
    print()

def _show_project_info(project):
    project_uid, project_group_name, project_gid, project_user_name = project.user_info()

    print("Project information:")
    print("  Project directory:   {}".format(project.root_dir))
    print("  Project ID:          {}".format(project.project_id))
    print("  Configuration file:  {}".format(project.config_path))
    print("  Temporary directory: {}".format(project.dot_dir))
    print()

    print("Project user information:")
    print("  User:                {} ({})".format(project_user_name, project_uid))
    print("  Group:               {} ({})".format(project_group_name, project_gid))
    print()

    print("Docker container information:")
    print("  Docker image ID:     {}".format(project.image_id))
    container_project_dir = project.settings.get("container-project-dir", project.default_container_project_dir)
    print("  Project directory:   {}".format(container_project_dir))
    print("  Temporary directory: {}".format(project.container_dot_dir))
    docker = project.settings.get("docker", None)
    docker_image = None if docker is None else docker.get("image", None)
    if docker is None:
        print("  Docker base image:   not configured")
    else:
        print("  Docker base image:   {}".format(docker["image"]))
    print()

    print("IBT status:")
    print("  Temporary directory: {}".format("exists" if os.path.isdir(project.dot_dir) else "does not exist"))
    print("  Docker image:        {}".format("built" if docker_image_exists(project.image_id) else "not built"))

    volumes = project.settings.get("volumes", None)
    if volumes is not None and len(volumes) > 0:
        print("\nProject volumes:")
        for key in sorted(volumes):
            local_dir = project.resolve_local_path(key)
            print("  {} = {}".format(local_dir, volumes[key]))

    aliases = project.settings.get("aliases", None)
    if aliases is not None and len(aliases) > 0:
        print("\nProject aliases:")
        for key in sorted(aliases):
            alias = aliases[key]
            if isinstance(alias, list):
                print("  {}:".format(key))
                for line in alias:
                    print("  - {}".format(line))
            else:
                print("  {} = {}".format(key, alias))

class InfoCommand(Command):
    def __init__(self):
        super(InfoCommand, self).__init__("info", requires_project=False)

    def add_subparser(self, subparsers):
        p = subparsers.add_parser(self.name, help="Show configuration information")
        p.set_defaults(obj=self, handler=self.run)

    def run(self, ctx, _):
        locations = []
        project = Project.read(ctx.working_dir, locations)

        show_banner()
        _show_system_info(ctx)

        if project is None:
            print("No project found; looked in:")
            for location in locations:
                print("  {}".format(location))
            print()
        else:
            _show_project_info(project)

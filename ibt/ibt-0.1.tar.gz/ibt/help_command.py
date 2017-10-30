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
from ibt.project import Project
from ibt.util import get_commands, show_banner

# Yes, this is a hack
# I'm too lazy to refactor the command classes for now
def _get_command_help(command):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    command.add_subparser(subparsers)
    return subparsers._get_subactions()[0].help

class HelpCommand(Command):
    def __init__(self):
        super(HelpCommand, self).__init__("help", requires_project=False)

    def add_subparser(self, subparsers):
        p = subparsers.add_parser(self.name, help="Display summary of standard commands")
        p.set_defaults(obj=self, handler=self.run)

    def run(self, ctx, args):
        show_banner()

        commands = get_commands()

        project = Project.read(ctx.working_dir)
        if project is None:
            has_aliases = False
        else:
            aliases = project.settings.get("aliases", None)
            has_aliases = aliases is not None and len(aliases) > 0

        max_name_len = 0
        for name in commands:
            if len(name) > max_name_len:
                max_name_len = len(name)

        if has_aliases:
            for key in aliases:
                if len(key) > max_name_len:
                    max_name_len = len(key)

        print("Commands:")
        for name in sorted(commands):
            command = commands[name]
            help = _get_command_help(command)
            print("  {}  {}".format(name.ljust(max_name_len), help))

        if has_aliases:
            print("\nProject aliases:")
            for key in sorted(aliases):
                alias = aliases[key]
                if isinstance(alias, list):
                    print("  {}:".format(key))
                    for line in alias:
                        print("  - {}".format(line))
                else:
                    print("  {}  {}".format(key.ljust(max_name_len), alias))

        print("")

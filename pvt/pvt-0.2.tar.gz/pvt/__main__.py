##################################################
# Copyright (C) 2017, All rights reserved.
##################################################

from __future__ import print_function
import argparse
import os
import sys

from pyprelude.file_system import make_path

from pvt import __description__, __project_name__, __version__
from pvt.config import Config
from pvt.exceptions import Informational
from pvt.project import Project

_SETUP_COMMANDS = [
    ("build", "Build package using setup.py in virtual environment", ["build"]),
    ("test", "Test package using setup.py in virtual environment", ["test"]),
    ("sdist", "Create package distribution using setup.py in virtual environment", ["sdist"]),
    ("upload", "Build, test, create and upload package using setup.py in virtual environment", ["build", "test", "sdist", "upload"])
]

def _do_init(config, args):
    project = Project.find(config, args.search_dir)
    project.initialize(force=args.force)
    print("Initialized virtual environment for {} in {}".format(project.project_dir, project.env_dir))

def _do_uninit(config, args):
    project = Project.find(config, args.search_dir)
    project.uninitialize()
    print("Uninitialized virtual environment for {} in {}".format(project.project_dir, project.env_dir))

def _do_show(config, args):
    project = Project.find(config, args.search_dir)

    print("Project directory: {}".format(project.project_dir))

    if os.path.isdir(project.env_dir):
        print("Virtual environment directory: {}".format(project.env_dir))
    else:
        print("Virtual environment not created")

    if os.path.isdir(project.bin_dir):
        print("Scripts directory: {}".format(project.bin_dir))
        script_names = os.listdir(project.bin_dir)
        if len(script_names) > 0:
            print("Installed scripts:")
            for script_name in sorted(script_names):
                print("  {}".format(script_name))

def _do_exec(config, args):
    project = Project.find(config, args.search_dir)
    args = args.command[:]
    script_name = args.pop(0)
    project.execute_script(script_name, args)

def _do_install(config, args):
    project = Project.find(config, args.search_dir)
    project.execute_script("pip", ["install", "--editable", project.project_dir])

def _add_search_dir_arg(parser, default):
    parser.add_argument(
        "--search-dir",
        "-d",
        type=make_path,
        default=make_path(default),
        help="Location from which to search for project")

def _main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    config_dir = make_path(os.path.expanduser(os.environ.get("PVT_DIR", "~/.pvt")))
    config = Config(config_dir)

    default_search_dir = os.getcwd()

    parser = argparse.ArgumentParser(prog=__project_name__, description=__description__)
    parser.add_argument(
        "--version",
        action="version",
        version="{} version {}".format(__project_name__, __version__))

    subparsers = parser.add_subparsers(help="subcommand help")

    init_parser = subparsers.add_parser("init", help="Initialize virtual environment for current project")
    init_parser.set_defaults(func=_do_init)
    _add_search_dir_arg(init_parser, default_search_dir)
    init_parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force overwrite of virtual environment directory if it already exists")

    uninit_parser = subparsers.add_parser("uninit", help="Uninitialize virtual environment for current project")
    uninit_parser.set_defaults(func=_do_uninit)
    _add_search_dir_arg(uninit_parser, default_search_dir)

    show_parser = subparsers.add_parser("show", help="Show information about current virtual environment")
    show_parser.set_defaults(func=_do_show)
    _add_search_dir_arg(show_parser, default_search_dir)

    exec_parser = subparsers.add_parser("exec", help="Execute command line in virtual environment context")
    exec_parser.set_defaults(func=_do_exec)
    _add_search_dir_arg(exec_parser, default_search_dir)
    exec_parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Command line to execute")

    install_parser = subparsers.add_parser("install", help="Install or reinstall current package into virtual environment in editable mode")
    install_parser.set_defaults(func=_do_install)
    _add_search_dir_arg(install_parser, default_search_dir)

    for command, help, actions in _SETUP_COMMANDS:
        command_parser = subparsers.add_parser(command, help=help)
        command_parser.set_defaults(
            func=lambda config, args, actions=actions: Project.find(
                config,
                args.search_dir).execute_setup_actions(actions))
        _add_search_dir_arg(command_parser, default_search_dir)

    args = parser.parse_args(argv)
    try:
        args.func(config, args)
    except Informational as e:
        print(e.message)
        sys.exit(1)

if __name__ == "__main__":
    _main()
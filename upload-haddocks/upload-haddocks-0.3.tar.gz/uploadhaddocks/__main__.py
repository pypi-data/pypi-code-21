############################################################
#
# uploadhaddocks.__main__
# Copyright (C) 2017, Richard Cook
# Released under MIT License
# https://github.com/rcook/upload-haddocks
#
############################################################

from __future__ import print_function
import argparse
import os
import sys

from pyprelude.file_system import make_path

from uploadhaddocks import __description__, __project_name__, __version__
from uploadhaddocks.util import upload_haddocks

def _parse_path(p):
    return make_path(os.getcwd(), os.path.expanduser(p))

def _parse_file_must_exist(path):
    path = _parse_path(path)
    if not os.path.isfile(path):
        raise argparse.ArgumentTypeError("File {} does not exist".format(path))
    return path

def _parse_dir_must_exist(path):
    path = _parse_path(path)
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError("Directory {} does not exist".format(path))
    return path

def _main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument("--version", action="version", version="{} version {}".format(__project_name__, __version__))
    parser.add_argument(
        "--creds",
        "-c",
        metavar="CREDENTIALSPATH",
        dest="credentials_path",
        default=_parse_path("~/.stack/upload/credentials.json"),
        type=_parse_file_must_exist,
        help="path to Stack credentials file")
    parser.add_argument(
        "--project-dir",
        "-p",
        metavar="PROJECTDIR",
        dest="project_dir",
        default=_parse_path(os.getcwd()),
        type=_parse_dir_must_exist,
        help="path to project")
    args = parser.parse_args()
    upload_haddocks(args.credentials_path, args.project_dir)

if __name__ == "__main__":
    _main()

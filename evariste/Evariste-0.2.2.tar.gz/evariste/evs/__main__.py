#!/bin/env python3

# Copyright Louis Paternault 2015
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Command line client to :mod:`evs`"""

import os

import argdispatch

import evariste

def _execlp(program, args):
    """Call :func:`os.execlp`, adding `program` as the first argument to itself."""
    return os.execlp(program, program, *args)

def commandline_parser():
    """Return a command line parser."""

    parser = argdispatch.ArgumentParser(
        prog="evs",
        description=(
            "Helper script for the evariste tool."
            ),
        formatter_class=argdispatch.RawTextHelpFormatter,
        )

    parser.add_argument(
        '--version',
        action='version',
        help='Show version',
        version='%(prog)s ' + evariste.VERSION
        )

    subparsers = parser.add_subparsers(
        title="Subcommands",
        description=(
            "List of available subcommands, either built-in, or gathered from `evs-*` binaries."
            ),
        )
    subparsers.required = True
    subparsers.dest = "subcommand"
    subparsers.add_submodules("evariste.evs")
    subparsers.add_prefix_executables("evs-")

    return parser

def main():
    """Main function"""

    commandline_parser().parse_args()

if __name__ == "__main__":
    main()

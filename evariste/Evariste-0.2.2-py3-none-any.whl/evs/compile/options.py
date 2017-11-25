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

"""Command line options"""

import argparse
import logging
import os
import sys
import textwrap

import evariste
from evariste import VERSION
from evariste.setup import Setup

LOGGER = logging.getLogger(evariste.__name__)
LOGGING_LEVELS = {
    -1: 100, # Quiet
    0: logging.WARNING,
    1: logging.INFO,
    2: logging.DEBUG,
    }

def _get_logging_level(verbose):
    """Turn command line verbosity into :mod:`LOGGING` verbosity."""
    if verbose in LOGGING_LEVELS:
        return LOGGING_LEVELS[verbose]
    if verbose is None:
        return LOGGING_LEVELS[0]
    if verbose > max(LOGGING_LEVELS.keys()):
        return LOGGING_LEVELS[max(LOGGING_LEVELS.keys())]
    raise NotImplementedError()

def _setup_type(name):
    """Check the argument and return its value.

    The argument must be an existing file.
    """
    if not os.path.exists(name):
        raise argparse.ArgumentTypeError(
            "File '{}' does not exist.".format(name)
            )
    if not os.path.isfile(name):
        raise argparse.ArgumentTypeError(
            "File '{}' is not a file.".format(name)
            )
    return name

def _itemgetint(value):
    """Return the first value of list, converted to an int."""
    try:
        return int(value[0])
    except ValueError:
        raise argparse.ArgumentTypeError(
            "Argument type should be an integer ('{}' is not).".format(value[0])
            )

class Options(argparse.Namespace):
    """Namespace of command line options.

    Added ability to iterate over option names.
    """
    # pylint: disable=too-few-public-methods

    def __str__(self):
        return str(dict([
            (attr, getattr(self, attr))
            for attr in dir(self)
            if not attr.startswith("_")
            ]))

    def __iter__(self):
        for attr in dir(self):
            if not attr.startswith("_"):
                yield attr

class Default:
    """Choose appropriate value given command line, setup file, etc.

    - If user set a value in the command line, it is used.
    - Othewise, if value is set in the ``arguments`` section of the setup file,
      use it.
    - At last, use the hard-coded default value defined in this module.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, name, defaultvalue, process_setup, process_arg):
        self.name = name
        self.defaultvalue = defaultvalue
        self.process_setup = process_setup
        self.process_arg = process_arg

    def __repr__(self):
        return "{}({}, {}, {}, {})".format(
            self.__class__.__name__,
            self.name,
            self.defaultvalue,
            self.process_setup,
            self.process_arg,
            )

    def get_value(self, value, setup):
        """Return the correct value, given the default values.

        :param str value: Value provided by the user.
        :param dict setup: The ``arguments`` section of the setup file, as a
            dictionary.
        """
        if value is not None:
            return self.process_arg(value)
        if self.name in setup:
            return self.process_setup(setup[self.name])
        return self.defaultvalue

class ArgumentParser(argparse.ArgumentParser):
    """Argument parser, using values from setup file as default values."""

    def __init__(self, *args, **kwargs):
        self.default = {}
        super().__init__(*args, **kwargs)

    def add_argument(self, *args, **kwargs):
        """This function adds two arguments to the value of its parent class.

        :param function process_arg: Function used to process command line
            argument (e.g. if argument is to be interpreted as an integer, this
            can be :func:`int`).
        :param function process_setup: Same usage, but is given as argument the
            value read from the setup file.
        """
        default = kwargs.pop("default", None)
        process_arg = kwargs.pop("process_arg", lambda x: x)
        process_setup = kwargs.pop("process_setup", lambda x: x)
        kwargs['default'] = None

        action = super().add_argument(*args, **kwargs)
        self.default[action.dest] = Default(action.dest, default, process_setup, process_arg)
        return action

    def parse_args(self, *args, **kwargs):
        """Parse user arguments, using setup options as default values."""
        try:
            namespace = super().parse_args(*args, **kwargs)

            # Process setup
            setup = vars(Setup.from_file(namespace.setup)).get('arguments', dict())

            # Set default values
            for attr in namespace:
                setattr(
                    namespace,
                    attr,
                    self.default[attr].get_value(
                        getattr(namespace, attr),
                        setup=setup,
                        ),
                    )

            # Process --verbose and --quiet
            if namespace.quiet:
                namespace.verbose = -1
            LOGGER.setLevel(_get_logging_level(namespace.verbose))

            return namespace
        except argparse.ArgumentTypeError as error:
            sys.stderr.write(str(error))
            sys.stderr.write("\n")
            sys.exit(2)

def commandline_parser():
    """Return a command line parser."""

    parser = ArgumentParser(
        prog="evariste",
        description=(
            "Recursively compile files in a directory, and render result."
            ),
        epilog=(
            "Note that `evariste ARGS` and `evs compile ARGS` are the same command."
            ),
        formatter_class=argparse.RawTextHelpFormatter,
        )

    parser.add_argument(
        '--version',
        help='Show version',
        action='version',
        version='%(prog)s ' + VERSION
        )

    parser.add_argument(
        "-v", "--verbose",
        help='Verbose. Repeat for more details.',
        action='count',
        )

    parser.add_argument(
        "-q", "--quiet",
        help='Quiet. Does not print anything to standard output.',
        action='store_true',
        default=False,
        )

    parser.add_argument(
        "-j", "--jobs",
        help=(
            "Specify the number of jobs to run simultaneously. Default is one "
            "more than the number of CPUs. "
            ),
        action='store',
        nargs=1,
        default=os.cpu_count()+1,
        process_setup=int,
        process_arg=_itemgetint,
        )

    parser.add_argument(
        "-B", "--always-compile",
        dest='always_compile',
        help='Unconditionally make all targets',
        action='store_true',
        default=False,
        process_setup=bool,
        )

    parser.add_argument(
        'setup',
        metavar="SETUP",
        help=textwrap.dedent("""
            Setup file to process.
            """),
        type=_setup_type,
        )

    return parser

def get_options():
    """Return the namespace of command line options."""
    return commandline_parser().parse_args(namespace=Options())

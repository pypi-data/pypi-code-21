# Copyright Louis Paternault 2016
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

"""Perform operations on cache."""

import argparse
import logging
import os
import sys
import textwrap

from evariste.cache import Cache
from evariste.errors import EvaristeError
from evariste.setup import Setup
from evariste.utils import expand_path

LOGGER = logging.getLogger(__name__)

def _cache_type(name):
    """Check the argument and return its value.

    The argument must be an existing file or directory.
    """
    if not os.path.exists(name):
        raise argparse.ArgumentTypeError(
            "File '{}' does not exist.".format(name)
            )
    return name

def commandline_parser():
    """Return a command line parser."""

    parser = argparse.ArgumentParser(
        prog="evs cache",
        description="Perform operations on cache.",
        formatter_class=argparse.RawTextHelpFormatter,
        )

    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument(
        'cache',
        metavar="CACHE",
        help=textwrap.dedent("""
            Cache to process.

            If neither '--setup' nor '--dir' options are provided, implicit '--setup' is used if argument is a file, and implicit '--dir' is used if argument is a directory.
            """),
        type=_cache_type,
        )
    group = parent.add_mutually_exclusive_group()
    group.add_argument(
        '-s',
        '--setup',
        help="Argument is considered to be a setup file; cache directory is deduced from it.",
        action='store_true',
        )
    group.add_argument(
        '-d',
        '--dir',
        help="Argument is considered to be the cache directory.",
        action='store_true',
        )

    subparsers = parser.add_subparsers(
        description="",
        dest="command",
        )
    subparsers.required = True

    clear = subparsers.add_parser(
        "clear",
        description="Delete cache.",
        parents=[parent],
        help="Delete cache.",
        )
    clear.set_defaults(command=do_clear)

    console = subparsers.add_parser(
        "console",
        description="Load cache and start an interactive console, with access to this cache.",
        parents=[parent],
        help="Load cache and start an interactive console.",
        )
    console.set_defaults(command=do_console)

    dump = subparsers.add_parser(
        "dump",
        description="Dump cache. For more control over cache, see the 'console' subcommand.",
        parents=[parent],
        help="Dump cache (print its reprensentation)."
        )
    dump.set_defaults(command=do_dump)

    return parser

def cache_path(options):
    """Return the path of the cache."""
    if options.setup:
        setup = Setup.from_file(options.cache)
        if setup['setup']['cachedir'] is None:
            return os.path.join(
                os.path.dirname(options.cache),
                '.{}.cache'.format(os.path.basename(options.cache)),
                )
        else:
            return os.path.join(
                os.path.dirname(options.cache),
                expand_path(setup['setup']['cachedir']),
                )
    else:
        return options.cache

def get_cache_class(options):
    """Return the :class:`Cache` class corresponding to the setup file."""
    # pylint: disable=unused-argument
    return Cache

def get_cache(options):
    """Return the :class:`Cache` object corresponding to the setup file."""
    if options.setup:
        setup = Setup.from_file(options.cache)
    else:
        setup = None

    return get_cache_class(options)(
        cachedir=cache_path(options),
        setup=setup,
        )

def do_console(namespace):
    """Execute the `evs cache console` command."""
    cache = get_cache(namespace)

    try:
        import ipdb as pdb
    except ImportError:
        print("""You can install the `ipdb` package to get an enhanced Python debugger.""")
        import pdb

    # pylint: disable=unused-variable
    version = cache.version
    plugin = cache.shared.plugin
    tree = cache.shared.tree

    print(textwrap.dedent("""\
        You have access to the following variables. You can modify value of variables marked as 'read-only', but their value will not be written into cache:
        - cache: the `Cache` object.
        - version: the cache version (read-only).
        - plugin: the cached plugin information.
        - tree: the cached tree information.

        By default, nothing is written into cache. Use `cache.close()` if you want to. It is possible to write malformed cache data, which cannot be read again. If so, you can use `evs cache clear` to remove cache completely.

        Type of variables `plugin` and `tree` are custom types. To get a read-only version as a dictonary, use `vars(plugin)` and `vars(tree)`.

        Use `Ctrl-D` or `exit()` to leave the debugger.
        """))

    pdb.set_trace()

def do_dump(namespace):
    """Execute the `evs cache dump` command."""
    cache = get_cache(namespace)

    dump = {'version': cache.version}
    dump.update({
        base: getattr(cache.shared, base)
        for base
        in cache.dataname
        })

    from pprint import pprint
    pprint(dump)

def do_clear(namespace):
    """Execute the `evs cache clear` command."""
    get_cache_class(namespace).clear(cache_path(namespace))

def parse_options(args):
    """Parse options, and perform some post-processing."""
    argumentparser = commandline_parser()
    options = argumentparser.parse_args(args)

    # Processing --setup/--dir options
    if options.setup:
        if not os.path.isfile(options.cache):
            argumentparser.error((
                "Argument '{}' provided with options '--setup' must be a file."
                ).format(options.cache))
    if options.dir:
        if not os.path.isdir(options.cache):
            argumentparser.error((
                "Argument '{}' provided with options '--dir' must be a directory."
                ).format(options.cache))
    if not (options.setup or options.dir):
        options.setup = os.path.isfile(options.cache)
        options.dir = os.path.isdir(options.cache)

    return options

def main(args=None):
    """Main function: run from command line."""
    options = parse_options(args)
    try:
        options.command(options)
    except EvaristeError as error:
        LOGGER.error(str(error))
        sys.exit(1)

if __name__ == "__main__":
    main()

u"""
Copyright 2015-2017 Hermann Krumrey

This file is part of kudubot.

kudubot is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

kudubot is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with kudubot.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import with_statement
from __future__ import absolute_import
import os
import sys
import time
import logging
import argparse
import traceback
from kudubot import version
from kudubot.exceptions import InvalidConfigException
from kudubot.connections.Connection import Connection
from kudubot.config.GlobalConfigHandler import GlobalConfigHandler
from io import open
from itertools import ifilter


# noinspection PyUnresolvedReferences
def main():  # pragma: no cover
    u"""
    The Main Method of the Program that starts the Connection Listener in
    accordance with the command line arguments
    """
    print u"Kudubot Version " + version

    args = parse_args()
    if not os.path.isdir(args.config):
        print args.config
        print u"Config directory does not exist"
        sys.exit(1)

    # noinspection PyUnresolvedReferences
    try:

        config_handler = GlobalConfigHandler(args.config)
        initialize_logging(
            args.quiet,
            args.verbose,
            args.debug,
            config_handler,
            args.connection.lower()
        )
        connection = initialize_connection(
            args.connection.lower(),
            config_handler
        )

        connection.listen()

    except KeyboardInterrupt:
        print u"\nBye"

    except BaseException, e:
        crashfile = os.path.join(
            GlobalConfigHandler().logfile_directory,
            u"crashes"
        )
        with open(crashfile, u'a') as crashlog:
            crashlog.write(u"Crash@" + unicode(time.time()) + u": " + unicode(e))
            crashlog.write(traceback.format_exc())
        raise e


def initialize_connection(identifier,
                          config_handler):  # pragma: no cover
    u"""
    Loads the connection for the specified identifier
    If the connection was not found in the local configuration,
    the program exits.

    :param identifier: The identifier for the Connection
    :param config_handler: The config handler to use
                           to determine file paths etc.
    :return: The Connection object
    """

    try:
        config_handler.validate_config_directory()
    except InvalidConfigException, e:
        print u"Loading configuration for service failed:"
        print unicode(e)
        sys.exit(1)

    connections = config_handler.load_connections()
    services = config_handler.load_services()

    try:
        connection_type = list(ifilter(
            lambda x: x.define_identifier() == identifier,
            connections
        ))[0]
        return connection_type(services, config_handler)

    except IndexError:
        print u"Connection Type " + identifier +
              u" is not implemented or imported using the config file"
        sys.exit(1)
    except InvalidConfigException, e:
        print u"Connection Configuration failed:"
        print unicode(e)
        sys.exit(1)


def initialize_logging(quiet, verbose, debug,
                       config_handler,
                       connection_name):
    u"""
    Initializes the logging levels and files for the program.
    If neither the verbose or debug flags were provided,
    the logging level defaults to WARNING.
    Log files for ERROR, WARNING, DEBUG and INFO are always generated.
    If the size of a previous log file exceeds 1MB,
    the file is renamed and a new one is created.

    :param quiet: Can be set to disable all logging to the console.
                  Text logs are still done however.
    :param verbose: Flag that determines if the verbose mode
                    is switched on ~ INFO
    :param debug: Flag that determines if the debug mode is on ~ DEBUG
    :param config_handler: The config handler used to determine
                           the logging directory location
    :param connection_name: The name of the connection to log
    """

    stdout_handler = logging.StreamHandler(stream=sys.stdout)

    if debug:
        stdout_handler.setLevel(logging.DEBUG)
    elif verbose:
        stdout_handler.setLevel(logging.INFO)
    elif quiet:
        stdout_handler.setLevel(logging.CRITICAL)
    else:
        stdout_handler.setLevel(logging.WARNING)

    logfile = os.path.join(config_handler.logfile_directory,
                           connection_name + u".log")

    if os.path.isfile(logfile):
        if os.path.getsize(logfile) > 1000000:
            os.rename(logfile, logfile + u"." + unicode(time.time()))

    logfile_handler = logging.FileHandler(logfile)
    logfile_handler.setLevel(logging.DEBUG)

    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[stdout_handler, logfile_handler]
    )


def parse_args():  # pragma: no cover
    u"""
    Parses the Command Line Arguments using argparse

    :return: The parsed arguments
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(u"connection", help=u"The Type of Connection to use")

    parser.add_argument(u"-v", u"--verbose", action=u"store_true",
                        help=u"Activates verbose output")
    parser.add_argument(u"-d", u"--debug", action=u"store_true",
                        help=u"Activates debug-level logging output")
    parser.add_argument(u"-q", u"--quiet", action=u"store_true",
                        help=u"Disables all text output")
    parser.add_argument(u"-c", u"--config",
                        default=os.path.join(os.path.expanduser(u"~"),
                                             u".kudubot"),
                        help=u"Overrides the configuration directory location")

    return parser.parse_args()

# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Tempmon commands
"""

from __future__ import unicode_literals, absolute_import

import datetime
import logging

from rattail import commands
from rattail.time import localtime, make_utc


log = logging.getLogger(__name__)


class ExportHotCooler(commands.ImportSubcommand):
    """
    Export data from Rattail-Tempmon to HotCooler
    """
    name = 'export-hotcooler'
    description = __doc__.strip()
    handler_spec = 'rattail_tempmon.hotcooler.importing.tempmon:FromTempmonToHotCooler'


class PurgeTempmon(commands.Subcommand):
    """
    Purge stale data from Tempmon database
    """
    name = 'purge-tempmon'
    description = __doc__.strip()

    def add_parser_args(self, parser):
        parser.add_argument('--keep', metavar='DAYS', required=True, type=int,
                            help="Number of days for which data should be kept.")
        parser.add_argument('--dry-run', action='store_true',
                            help="Go through the full motions and allow logging etc. to "
                            "occur, but rollback (abort) the transaction at the end.")

    def run(self, args):
        from rattail_tempmon.db import Session as TempmonSession, model as tempmon

        cutoff = localtime(self.config).date() - datetime.timedelta(days=args.keep)
        cutoff = localtime(self.config, datetime.datetime.combine(cutoff, datetime.time(0)))
        session = TempmonSession()

        readings = session.query(tempmon.Reading)\
                          .filter(tempmon.Reading.taken < make_utc(cutoff))
        count = readings.count()

        def purge(reading, i):
            session.delete(reading)
            if i % 200 == 0:
                session.flush()

        self.progress_loop(purge, readings, count=count, message="Purging stale readings")
        log.info("deleted {} stale readings".format(count))

        if args.dry_run:
            session.rollback()
            log.info("dry run, so transaction was rolled back")
        else:
            session.commit()
            log.info("transaction was committed")
        session.close()


class TempmonClient(commands.Subcommand):
    """
    Manage the tempmon-client daemon
    """
    name = 'tempmon-client'
    description = __doc__.strip()

    def add_parser_args(self, parser):
        subparsers = parser.add_subparsers(title='subcommands')

        start = subparsers.add_parser('start', help="Start daemon")
        start.set_defaults(subcommand='start')
        stop = subparsers.add_parser('stop', help="Stop daemon")
        stop.set_defaults(subcommand='stop')

        parser.add_argument('-p', '--pidfile',
                            help="Path to PID file.", metavar='PATH')
        parser.add_argument('-D', '--daemonize', action='store_true',
                            help="Daemonize when starting.")

    def run(self, args):
        from rattail_tempmon.client import make_daemon

        daemon = make_daemon(self.config, args.pidfile)
        if args.subcommand == 'start':
            daemon.start(args.daemonize)
        elif args.subcommand == 'stop':
            daemon.stop()


class TempmonServer(commands.Subcommand):
    """
    Manage the tempmon-server daemon
    """
    name = 'tempmon-server'
    description = __doc__.strip()

    def add_parser_args(self, parser):
        subparsers = parser.add_subparsers(title='subcommands')

        start = subparsers.add_parser('start', help="Start daemon")
        start.set_defaults(subcommand='start')
        stop = subparsers.add_parser('stop', help="Stop daemon")
        stop.set_defaults(subcommand='stop')

        parser.add_argument('-p', '--pidfile',
                            help="Path to PID file.", metavar='PATH')
        parser.add_argument('-D', '--daemonize', action='store_true',
                            help="Daemonize when starting.")

    def run(self, args):
        from rattail_tempmon.server import make_daemon

        daemon = make_daemon(self.config, args.pidfile)
        if args.subcommand == 'start':
            daemon.start(args.daemonize)
        elif args.subcommand == 'stop':
            daemon.stop()


class TempmonProblems(commands.Subcommand):
    """
    Email report(s) of various Tempmon data problems
    """
    name = 'tempmon-problems'
    description = __doc__.strip()

    def run(self, args):
        from rattail_tempmon import problems

        problems.disabled_probes(self.config, progress=self.progress)

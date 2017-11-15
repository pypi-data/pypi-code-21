##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Functions that control how the Zope appserver knits itself together.
"""
import asyncore
import logging
import os
import sys
import time

from zdaemon import zdoptions

import zope.app.appsetup.appsetup
import zope.processlifetime
import zope.app.appsetup.product
from zope.event import notify
from zope.server.taskthreads import ThreadedTaskDispatcher

CONFIG_FILENAME = "zope.conf"

class ZopeOptions(zdoptions.ZDOptions):

    logsectionname = None

    def default_configfile(self):
        # XXX: this probably assumes a monolithic zope 3 source tree
        # layout and isn't likely to work
        dir = os.path.normpath(
            os.path.join(os.path.dirname(__file__),
                         os.pardir, os.pardir, os.pardir, os.pardir))
        for filename in [CONFIG_FILENAME, CONFIG_FILENAME + ".in"]:
            filename = os.path.join(dir, filename)
            if os.path.isfile(filename):
                return filename
        return None



exit_status = None
def main(args=None):
    # Record start times (real time and CPU time)
    t0 = time.time()
    c0 = time.clock()

    setup(load_options(args))

    t1 = time.time()
    c1 = time.clock()
    logging.info("Startup time: %.3f sec real, %.3f sec CPU", t1-t0, c1-c0)

    run()
    sys.exit(exit_status or 0)


def debug(args=None):
    options = load_options(args)

    zope.app.appsetup.product.setProductConfigurations(
        options.product_config)

    zope.app.appsetup.config(options.site_definition)

    db = zope.app.appsetup.appsetup.multi_database(options.databases)[0][0]
    notify(zope.processlifetime.DatabaseOpened(db))
    return db


def run():
    try:
        global exit_status
        while asyncore.socket_map and exit_status is None:
            asyncore.poll(30.0)
    except KeyboardInterrupt:
        # Exit without spewing an exception.
        pass


def load_options(args=None):
    if args is None:
        args = sys.argv[1:]
    options = ZopeOptions()
    options.schemadir = os.path.dirname(os.path.abspath(__file__))
    options.realize(args)
    options = options.configroot

    if options and options.path:
        sys.path[:0] = [os.path.abspath(p) for p in options.path]
    return options


def setup(options):
    sys.setcheckinterval(options.check_interval)

    zope.app.appsetup.product.setProductConfigurations(
        options.product_config)
    options.eventlog()
    options.accesslog()
    for logger in options.loggers:
        logger()

    features = ('zserver',)
    # Provide the devmode, if activated
    if options.devmode:
        features += ('devmode',)
        logging.warning("Developer mode is enabled: this is a security risk "
            "and should NOT be enabled on production servers. Developer mode "
            "can be turned off in etc/zope.conf")

    zope.app.appsetup.config(options.site_definition, features=features)

    db = zope.app.appsetup.appsetup.multi_database(options.databases)[0][0]

    notify(zope.processlifetime.DatabaseOpened(db))

    task_dispatcher = ThreadedTaskDispatcher()
    task_dispatcher.setThreadCount(options.threads)

    for server in options.servers:
        server.create(task_dispatcher, db)

    notify(zope.processlifetime.ProcessStarting())

    return db

#!/usr/bin/env python
"""
PoolServer itself need two arguments. The first is the handler, which is a
callable object. The second is 'pool_size', which stands for the size of the
GreenThread Pool, that's eventlet.GreenPool, see below. The other arguments
will be passed to the handler.

For the handler, the first argument is a instance of eventlet.GreenPool, and
the other arguments are from the arguments of PoolServer.
"""
from __future__ import absolute_import, print_function

import time
import logging

import eventlet
from oslo_config import cfg
from oslo_log import log
from oslo_service import service

from bservices.contrib.server import PoolServer

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


def task(i):
    LOG.info("Get the number: {0}".format(i))


def handler(pool, interval=30):
    while True:
        for i in range(100):
            pool.spawn_n(task, i)
        time.sleep(interval)


def main(project="pool_server_example"):
    log.register_options(CONF)
    # log.set_defaults(default_log_levels=None)
    CONF(project=project)

    log.setup(CONF, project)
    eventlet.monkey_patch(all=True)

    server = PoolServer(handler, interval=10, pool_size=100)
    launcher = service.launch(CONF, server)
    launcher.wait()


if __name__ == '__main__':
    main()

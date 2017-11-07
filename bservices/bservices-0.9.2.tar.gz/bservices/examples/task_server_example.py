#!/usr/bin/env python
"""
TaskServer itself need two arguments. The first is the handler, which is a
callable object. The second is 'task_num', which stands for the number of the
task to start. The other arguments will be passed to the handler.

For the handler, the arguments are all from the TaskServer.
"""
from __future__ import absolute_import, print_function

import time
import logging

import eventlet
from oslo_config import cfg
from oslo_log import log
from oslo_service import service

from bservices.contrib.server import TaskServer

LOG = logging.getLogger(__name__)
CONF = cfg.CONF


def task(i):
    LOG.info("Get the number: {0}".format(i))


def handler(interval, data):
    while True:
        LOG.info("Start the task to handle the data: {0}".format(data))
        time.sleep(interval)


def main(project="pool_server_example"):
    log.register_options(CONF)
    # log.set_defaults(default_log_levels=None)
    CONF(project=project)

    log.setup(CONF, project)
    eventlet.monkey_patch(all=True)

    server = TaskServer(handler, task_num=100, interval=10, data="test")
    launcher = service.launch(CONF, server)
    launcher.wait()


if __name__ == '__main__':
    main()

#!/usr/bin/env python
"""
The handler of TCPServer only need two arguments.
The first is a socket object.
The second is the address of the client, like ("127.0.0.1", 39305).
"""
from __future__ import absolute_import, print_function

import logging

import eventlet
from oslo_config import cfg
from oslo_log import log
from oslo_service import service

from bservices.contrib.server import TCPServer

LOG = logging.getLogger(__name__)
CONF = cfg.CONF

cli_opts = [
    cfg.StrOpt("listen_ip", default='0.0.0.0'),
    cfg.IntOpt("listen_port", default=10000)
]
CONF.register_cli_opts(cli_opts)


def task(i):
    LOG.info("Get the number: {0}".format(i))


def handler(conn, client_addr):
    while True:
        LOG.info("Receive the connection from {0}".format(str(client_addr)))
        data = conn.recv(8192)
        if not data:
            LOG.info("The peer close the connection")
            return
        n = conn.send(data)
        LOG.info("Send {0} bytes".format(n))


def main(project="pool_server_example"):
    log.register_options(CONF)
    # log.set_defaults(default_log_levels=None)
    CONF(project=project)

    log.setup(CONF, project)
    eventlet.monkey_patch(all=True)

    server = TCPServer(handler, host=CONF.listen_ip, port=CONF.listen_port,
                       pool_size=10240)
    launcher = service.launch(CONF, server)
    launcher.wait()


if __name__ == '__main__':
    main()

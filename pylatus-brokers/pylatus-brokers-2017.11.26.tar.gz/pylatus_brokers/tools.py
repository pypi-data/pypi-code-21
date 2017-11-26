#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import constants as c


def get_hostport(address):
    if isinstance(address, (tuple, list)):
        host, port = address
    elif isinstance(address, str):
        if ':' in address:
            host, port = address.split(':')[:2]
        else:
            host, port = address, c.RABBITMQ_PORT
    else:
        host, port = c.RABBITMQ_HOST, c.RABBITMQ_PORT
    try:
        port = int(port)
    except ValueError:
        port = c.RABBITMQ_PORT
    return host, port

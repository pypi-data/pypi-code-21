#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
from agent.util.sentry import Sentry

sentry = Sentry()


def ip():
    global s, _ip
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        _ip = s.getsockname()[0]
    except Exception:
        sentry.client.captureException()
    finally:
        s.close()

    return _ip


def name():
    return socket.gethostname()

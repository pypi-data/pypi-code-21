# -*- coding: utf-8 -*-
import io
import os
import re
from .core import get_logger

logger = get_logger('p4rr0t007')


def match_loopback_address_from_etc_hosts_line(line):
    regex = re.compile(r'^\s*(?P<ipaddr>[:]{2}1|127[.]0[.]0[.]1)\s+(?P<hostname>[\w.-]+)\s*$', re.U)
    found = regex.search(line)
    if found:
        return found.groupdict()

    return {}


def get_etc_hosts():

    HOSTS_FILENAME = '/etc/hosts'
    lines = []

    if not os.path.isfile(HOSTS_FILENAME):
        return lines

    try:
        with io.open('/etc/hosts', 'rb') as fd:
            lines = fd.readlines()
    except Exception as e:
        logger.warning('Failed to read hosts file at "%s": %s', HOSTS_FILENAME, e)

    return dict(map(lambda match: (match['hostname'], match['ipaddr']), filter(bool, map(match_loopback_address_from_etc_hosts_line, lines))))


def hostname_seems_ipv4_address(hostname):
    return re.match('^(\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3})$', hostname) is not None

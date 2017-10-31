# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

import logging
from pkg_resources import resource_filename

from appdynamics.lib import default_log_formatter

# The following is a very basic logging config which outputs WARNING level logs to stderr.
try:
    logger = logging.getLogger('appdynamics')
    level = logging.WARNING
    logger.setLevel(level)
    logger.propagate = False
    handler = logging.StreamHandler()
    handler.setFormatter(default_log_formatter)
    handler.setLevel(level)
    logger.addHandler(handler)
except:
    pass


def get_reported_version():
    return 'Python Agent v%s (proxy v%s)' % (get_agent_version(), get_proxy_version())


def get_agent_version_file():
    return resource_filename('appdynamics', 'VERSION')


def get_proxy_version_file():
    return resource_filename('appdynamics_bindeps.proxy', 'VERSION')


def get_agent_version(noisy=True):
    return get_version(get_agent_version_file(), noisy)


def get_proxy_version(noisy=True):
    return get_version(get_proxy_version_file(), noisy)


def get_version(version_file, noisy=True):
    try:
        with open(version_file, 'r') as f:
            version = f.read().split('.')
            # controller expects all agent versions to be of the form 1.2.3.4, so pad as necessary
            version.extend(['0'] * (4 - len(version)))
            return '.'.join(version)
    except:
        if noisy:
            logging.getLogger('appdynamics.agent').exception("Couldn't parse build info.")
        return 'unknown'

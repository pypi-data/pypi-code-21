"""
PyRKube
~~~~~~~~~~~~~

Readonly wrapper for pykube with a different focus.
"""

import logging

from . import config, util, adict, exceptions, client, hosts, objects
from .exceptions import PyrKubeError, KubeConfigNotFound
from .client import KubeAPIClient, KubeInterfaceBase
from .hosts import PodHostname, StatefulPodHostname
from .objects import (
    Pod,
    ConfigMap,
    Secret,
    ReplicaSet,
    Deployment,
    DaemonSet,
    StatefulSet,
    Endpoint,
    Service,
    KubeApp,
    KubeApps
)

__title__ = 'pyrkube'
__version__ = '0.2.4'
__build__ = 0x000203
__author__ = "Joe Black <joe@valuphone.com>"
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2017 Joe Black'


logging.getLogger(__name__).addHandler(logging.NullHandler())

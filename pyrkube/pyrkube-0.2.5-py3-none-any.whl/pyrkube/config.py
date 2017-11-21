"""
pyrkube.config
~~~~~~~~~~~~~~

Configuration for pyrkube.

:copyright: (c) 2017 by Joe Black.
:license: Apache2.
"""

import os

LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG').upper()
ENVIRONMENT = os.getenv('ENVIRONMENT', 'dev')
DOMAIN = os.getenv('DNS_DOMAIN', 'cluster.local')

del os

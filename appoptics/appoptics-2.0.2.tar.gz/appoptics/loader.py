""" AppOptics instrumentation loader

Checks appoptics.config['inst_enabled'] and imports as requested. used by middleware
and djangoware.

Copyright (C) 2016 by SolarWinds, LLC.
All rights reserved.
"""
from appoptics import util

def _enabled(m):
    return util.config['inst_enabled'][m]


def load_inst_modules():
    if _enabled('memcache'):
        from appoptics import inst_memcache
    if _enabled('pymongo'):
        from appoptics import inst_pymongo
    if _enabled('sqlalchemy'):
        from appoptics import inst_sqlalchemy
    if _enabled('httplib'):
        from appoptics import inst_httplib
    if _enabled('redis'):
        from appoptics import inst_redis
    # additionally, in djangoware.py: 'django_orm', 'django_templates'

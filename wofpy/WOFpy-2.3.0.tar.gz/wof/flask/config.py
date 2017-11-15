from __future__ import (absolute_import, division, print_function)

class Config(object):
    DEBUG = False
    TESTING = False

class DevConfig(Config):
    DEBUG = True

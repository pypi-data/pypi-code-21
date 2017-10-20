# -*- coding: utf-8 -*-
import os
from datetime import timedelta
from plant import Node

node = Node(__file__).dir

RANDOM_SEED = os.urandom(36).encode('hex')

BASE_URL = os.environ.get('BASE_URL') or 'http://localhost:5000'
SECRET_KEY = os.environ.get('SECRET_KEY') or RANDOM_SEED
SESSION_TYPE = 'redis'
SESSION_COOKIE_SECURE = True
PERMANENT_SESSION_LIFETIME = timedelta(hours=6)
SESSION_KEY_PREFIX = 'p4rr0t007:session:'
DEBUG = False
LOCAL = False
DOMAIN = '127.0.0.1'

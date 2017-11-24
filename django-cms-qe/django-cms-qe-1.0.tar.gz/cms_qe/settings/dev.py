"""
Configuration for development.

Disables all security options.
"""

import os
from typing import List  # pylint: disable=unused-import

from .base import *  # pylint: disable=wildcard-import,unused-wildcard-import

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

DEBUG = True

META_SITE_PROTOCOL = 'http'

SECRET_KEY = '^xzhq0*q1+t0*ihq^^1wuyj3i%y#(38b7d-vlpkm-d(=!^uk6x'

SESSION_COOKIE_SECURE = False

SECURE_HSTS_SECONDS = 0

ALLOWED_HOSTS = ['localhost']

INSTALLED_APPS += [
    'debug_toolbar',
    'django_extensions',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

# Logging
# https://docs.djangoproject.com/en/1.11/topics/logging/

LOGGING['loggers'] = {
    '': {
        'level': 'INFO',
        'handlers': ['console'],
    },
}

# Caching
# https://docs.djangoproject.com/en/1.11/topics/cache/

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, '..', 'db.sqlite3'),
        'TEST': {
            'NAME': ':memory:',
        },
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

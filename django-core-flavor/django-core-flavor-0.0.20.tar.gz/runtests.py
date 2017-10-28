#!/usr/bin/env python

import os
import sys

import django

from django.conf import settings
from django.test.runner import DiscoverRunner


DEFAULT_SETTINGS = dict(
    SITE_NAME='test',
    USE_TZ=True,
    INSTALLED_APPS=(
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'oauth2_provider',
        'rest_framework',
        'core_flavor.apps.CoreAppConfig',
        'tests'
    ),
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'test'
        }
    },
    ROOT_URLCONF='tests.urls',
    REST_FRAMEWORK={
        'TEST_REQUEST_DEFAULT_FORMAT': 'json',
        'EXCEPTION_HANDLER':
        'core_flavor.drf.exceptions.verbose_exception_handler',
        'DEFAULT_PAGINATION_CLASS':
        'core_flavor.drf.pagination.CursorPageNumberPagination',
        'PAGE_SIZE': 10,
    },
    MIDDLEWARE=[
        'core_flavor.drf.middleware.VersioningMiddleware'
    ]
)


def runtests():
    if not settings.configured:
        settings.configure(**DEFAULT_SETTINGS)

    django.setup()

    parent = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, parent)

    failures = DiscoverRunner(
        verbosity=1,
        interactive=True,
        failfast=False)\
        .run_tests(['tests'])

    sys.exit(failures)


if __name__ == '__main__':
    runtests()

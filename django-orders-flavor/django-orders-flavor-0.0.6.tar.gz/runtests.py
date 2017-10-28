#!/usr/bin/env python

import os
import sys

import django

from django.conf import settings
from django.test.runner import DiscoverRunner


DEFAULT_SETTINGS = dict(
    USE_TZ=True,
    SITE_NAME='test',
    INSTALLED_APPS=(
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django_filters',
        'oauth2_provider',
        'paypal.standard.ipn',
        'rest_framework',
        'core_flavor.apps.CoreAppConfig',
        'countries.apps.CountriesAppConfig',
        'orders.apps.OrdersAppConfig',
        'tests'
    ),
    DATABASES={
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': 'test'
        }
    },
    ROOT_URLCONF='tests.urls',
    REST_FRAMEWORK={
        'DEFAULT_FILTER_BACKENDS': (
            'rest_framework_filters.backends.DjangoFilterBackend',
            'rest_framework.filters.OrderingFilter',
            'rest_framework.filters.SearchFilter'
        ),
        'DEFAULT_PAGINATION_CLASS':
        'core_flavor.drf.pagination.CursorPageNumberPagination',
        'PAGE_SIZE': 10,
        'TEST_REQUEST_DEFAULT_FORMAT': 'json'
    },
    MIDDLEWARE=[
        'core_flavor.drf.middleware.VersioningMiddleware'
    ],
    PAYPAL_BUSINESS='test',
    PAYPAL_TEST=True,
    TEMPLATES=[{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'OPTIONS': {
            'loaders': [
                'django.template.loaders.app_directories.Loader'
            ]
        }
    }]
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

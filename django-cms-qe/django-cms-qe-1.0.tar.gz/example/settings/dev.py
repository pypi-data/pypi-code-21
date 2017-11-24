
import os

from cms_qe.settings.dev import *


INSTALLED_APPS += [
    'example',
]

ROOT_URLCONF = 'example.urls'
WSGI_APPLICATION = 'example.wsgi.application'

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, '..', 'db.sqlite3'),
        'TEST': {
            'NAME': ':memory:',
        }
    }
}

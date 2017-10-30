import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'

INTERNAL_IPS = ['127.0.0.1']

LOGGING_CONFIG = None   # avoids spurious output in tests


# Application definition

INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'assets',
]

MEDIA_URL = 'http://localhost:7321/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'tests', 'cdn','media')
STATIC_URL = 'http://localhost:7321/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'tests', 'cdn','static')

MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'tests.urls'

TEMPLATES = [
    {
        'NAME': 'jinja2',
        'BACKEND': 'django_jinja.backend.Jinja2',
        'APP_DIRS': True,
        'DIRS': [os.path.join(BASE_DIR, 'tests', 'templates', 'jinja2')],
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
            ],
        },
    },
]

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'tests', 'static', 'manifest'),
    os.path.join(BASE_DIR, 'tests', 'static', 'standard'),
]

# Cache and database

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'second': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

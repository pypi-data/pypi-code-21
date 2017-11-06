# -*- coding: utf-8 -*-
# Django settings for crossix project.

import os

import getconf

# Paths
# =====
BASE_DIR = os.path.dirname(__file__)
CHECKOUT_DIR = os.path.dirname(BASE_DIR)


# Global configuration
# ====================

config = getconf.ConfigGetter('crossix', [
    '/etc/crossix/*.ini',
    os.path.join(CHECKOUT_DIR, 'local_settings.ini'),
    ])


APPMODE = config.get('app.mode', 'prod')
assert APPMODE in ('dev', 'dist', 'prod'), "Invalid application mode %s" % APPMODE


# Generic Django settings
# =======================

# SECURITY WARNING: keep the secret key used in production secret!
if APPMODE in ('dev', 'dist'):
    _default_secret_key = 'Dev only!!'
else:
    _default_secret_key = ''

SECRET_KEY = config.get('app.secret_key', _default_secret_key)


# Debug
# =====

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config.getbool('app.debug', APPMODE == 'dev')

if config.get('site.admin_mail'):
    ADMINS = (
        ("Cross-X admins", config.get('site.admin_mail')),
    )
    MANAGERS = ADMINS

if config.get('site.from_mail'):
    SERVER_EMAIL = config.get('site.from_mail')



# URLs
# ====

if APPMODE == 'dev':
    _default_url = 'http://example.org/'
else:
    _default_url = ''

ALLOWED_HOSTS = config.getlist('site.allowed_hosts')


# Loadable components
# ===================

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'crossix.registrations',
    'crossix.pages',
    'crossix',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
            ],
        },
    },
]

ROOT_URLCONF = 'crossix.urls'

if APPMODE == 'dev':
    # Avoid the need for collectstatic before running tests
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
else:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.CachedStaticFilesStorage'


# Database
# ========

_ENGINE_MAP = {
    'sqlite': 'django.db.backends.sqlite3',
    'mysql': 'django.db.backends.mysql',
    'postgresql': 'django.db.backends.postgresql_psycopg2',
}
_engine = config.get('db.engine', 'sqlite')
if _engine not in _ENGINE_MAP:
    raise ImproperlyConfigured(
        "DB engine %s is unknown; please choose from %s"
        % (_engine, ', '.join(sorted(_ENGINE_MAP.keys())))
    )
if _engine == 'sqlite':
    if APPMODE == 'dev':
        _default_db_name = os.path.join(CHECKOUT_DIR, 'dev', 'db.sqlite')
    else:
        _default_db_name = '/var/lib/crossix/db.sqlite'
else:
    _default_db_name = 'crossix'


DATABASES = {
    'default': {
        'ENGINE': _ENGINE_MAP[_engine],
        'NAME': config.get('db.name', _default_db_name),
        'HOST': config.get('db.host'),
        'PORT': config.get('db.port'),
        'USER': config.get('db.user'),
        'PASSWORD': config.get('db.password'),
    }
}

# Internationalization
# ====================

TIME_ZONE = config.get('i18n.tz', 'Europe/Paris')

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = config.get('i18n.language', 'fr-fr')

USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# ======================================

STATIC_URL = config.get('site.assets_url', '/assets/')
STATIC_ROOT = os.path.join(BASE_DIR, 'assets')


# Uploads
# =======

if APPMODE == 'dev':
    _default_media = os.path.join(CHECKOUT_DIR, 'dev', 'media')
else:
    _default_media = ''

MEDIA_ROOT = config.get('uploads.dir', _default_media)
SENDFILE_BACKEND = 'sendfile.backends.%s' % config.get('uploads.serve', 'simple')
SENDFILE_ROOT = os.path.join(MEDIA_ROOT, 'crossix')
SENDFILE_URL = config.get('uploads.internal_url', '/uploads/')

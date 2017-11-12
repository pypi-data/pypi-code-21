from settings import *
# RENAME THIS FILE local_settings.py IF YOU NEED TO CUSTOMIZE SOME SETTINGS
# BUT DO NOT COMMIT
TEST_PERFORMANCE = False

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'django_restframework_gis',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': '127.0.0.1',
        'PORT': '5432'
    },
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',

    # geodjango widgets
    #'olwidget',

    # admin
    #'grappelli',
    'django.contrib.admin',

    # rest framework
    'rest_framework',
    'rest_framework_gis',

    # test app
    'django_restframework_gis_tests',
    'django_extensions'
)

POSTGIS_VERSION = (2, 1)
GDAL_LIBRARY_PATH = '/usr/lib/libgdal.so.1'

#REST_FRAMEWORK = {
#     'DEFAULT_RENDERER_CLASSES': (
#         'drf_ujson.renderers.UJSONRenderer',
#     ),
#     'DEFAULT_PARSER_CLASSES': (
#        'drf_ujson.parsers.UJSONParser',
#     ),
#}

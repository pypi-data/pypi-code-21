import os

from shuup.utils.setup import Setup
from shuup_workbench.settings.utils import DisableMigrations


#-------------------------------------------------------------------------------
# directories
#-------------------------------------------------------------------------------

MEDIA_URL = '/media/'
STATIC_URL = '/static/'

#-------------------------------------------------------------------------------
# shuup settings
#-------------------------------------------------------------------------------

SHUUP_PRICING_MODULE = 'customer_group_pricing'

SHUUP_REGISTRATION_REQUIRES_ACTIVATION = False

SHUUP_SETUP_WIZARD_PANE_SPEC = [
    'shuup.admin.modules.shops.views:ShopWizardPane',
    'shuup.admin.modules.service_providers.views.PaymentWizardPane',
    'shuup.admin.modules.service_providers.views.CarrierWizardPane',
    'shuup.xtheme.admin_module.views.ThemeWizardPane',
    'shuup.admin.modules.content.views.ContentWizardPane',
    'shuup.admin.modules.sample_data.views.SampleObjectsWizardPane',
]

# shuup error_handlers are suppressing any debug info
SHUUP_ERROR_PAGE_HANDLERS_SPEC = None

SHUUP_DEFAULT_THEME = 'shuup.themes.classic_gray'

SHUUP_SIMPLE_SEARCH_LIMIT = 150

#-------------------------------------------------------------------------------
# django
#-------------------------------------------------------------------------------

DEBUG = True
SECRET_KEY = '0000'
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'
SITE_ID = 1

#-------------------------------------------------------------------------------
# applications
#-------------------------------------------------------------------------------

INSTALLED_APPS_SHUUP_DEFAULT = [
    # django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # external apps that needs to be loaded before Shuup
    'easy_thumbnails',
    # shuup
    'shuup.addons',
    'shuup.admin',
    'shuup.api',
    'shuup.core',
    'shuup.default_tax',
    'shuup.front',
    'shuup.front.apps.auth',
    'shuup.front.apps.carousel',
    'shuup.front.apps.customer_information',
    'shuup.front.apps.personal_order_history',
    'shuup.front.apps.saved_carts',
    'shuup.front.apps.registration',
    'shuup.front.apps.simple_order_notification',
    'shuup.front.apps.simple_search',
    'shuup.front.apps.recently_viewed_products',
    'shuup.notify',
    'shuup.simple_cms',
    'shuup.customer_group_pricing',
    'shuup.campaigns',
    'shuup.simple_supplier',
    'shuup.order_printouts',
    'shuup.testing',
    'shuup.utils',
    'shuup.xtheme',
    'shuup.reports',
    'shuup.default_reports',
    'shuup.regions',
    'shuup.importer',
    'shuup.default_importer',
    SHUUP_DEFAULT_THEME,
    # external apps
    'bootstrap3',
    'django_countries',
    'django_jinja',
    'filer',
    'registration',
    'rest_framework',
    'rest_framework_swagger',
]

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'shuup.front.middleware.ProblemMiddleware',
    'shuup.front.middleware.ShuupFrontMiddleware',
]

#-------------------------------------------------------------------------------
# localization
#-------------------------------------------------------------------------------

LANGUAGES = [
    ('en', 'English'),
    ('fi', 'Finnish'),
    ('ja', 'Japanese'),
]
LANGUAGE_CODE = 'en'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

PARLER_DEFAULT_LANGUAGE_CODE = 'en'
PARLER_LANGUAGES = {
    None: [dict(code=code, name=name) for (code, name) in LANGUAGES],
    'default': {
        'hide_untranslated': False,
    }
}

#-------------------------------------------------------------------------------
# templates
#-------------------------------------------------------------------------------

template_context_processors = [
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.core.context_processors.tz',
]

TEMPLATES = [
    {
        'BACKEND': 'django_jinja.backend.Jinja2',
        'APP_DIRS': True,
        'OPTIONS': {
            'match_extension': '.jinja',
            'context_processors': template_context_processors,
            'newstyle_gettext': True,
            'environment': 'shuup.xtheme.engine.XthemeEnvironment',
        },
        'NAME': 'jinja2',
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': template_context_processors,
            'debug': DEBUG,
        }
    },
]

#-------------------------------------------------------------------------------
# URLs
#-------------------------------------------------------------------------------

ROOT_URLCONF = 'shuup_workbench.urls'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

#-------------------------------------------------------------------------------
# REST
#-------------------------------------------------------------------------------

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'shuup.api.permissions.ShuupAPIPermission',
    )
}

JWT_AUTH = {
    'JWT_ALLOW_REFRESH': True,
}

SWAGGER_SETTINGS = {
    'SUPPORTED_SUBMIT_METHODS': [
        'get',
    ],
}

#-------------------------------------------------------------------------------
# suppress deprecation warnings
#-------------------------------------------------------------------------------

LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {'format': '[%(asctime)s] (%(name)s:%(levelname)s): %(message)s'},
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'shuup': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': True},
    }
}

#-------------------------------------------------------------------------------
# test settings
#-------------------------------------------------------------------------------

DEFAULT_FROM_EMAIL = 'no-reply@example.com'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

if os.environ.get('IS_SHUUP_TEST') is 'true':
    MIGRATION_MODULES = DisableMigrations()
    SOUTH_TESTS_MIGRATE = False


def update_globals():
    def configure(setup):
        setup.commit(globals())

    globals_new = Setup.configure(configure)
    globals().update(globals_new)

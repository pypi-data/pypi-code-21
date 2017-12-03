import os

from shuup.addons import add_enabled_addons
from django_jinja.builtins import DEFAULT_EXTENSIONS
from shuup_testutils.settings_base import *

#------------------------------------------------------------------------------
# env vars
#------------------------------------------------------------------------------

IS_GITLAB_CI_TEST = os.environ.get('CI_SERVER') == 'yes'

IS_SKIP_INTEGRATION_TEST = os.environ.get('DJANGO_SCATL_IS_SKIP_INTEGRATION_TEST') == 'true'

#------------------------------------------------------------------------------
# directories
#------------------------------------------------------------------------------

BASE_DIR = os.path.dirname(__file__)
# noinspection PyUnresolvedReferences
MEDIA_ROOT = os.path.join(BASE_DIR, 'var', 'media')
# noinspection PyUnresolvedReferences
STATIC_ROOT = os.path.join(BASE_DIR, 'var', 'static')

#------------------------------------------------------------------------------
# database
#------------------------------------------------------------------------------

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'scatl',
        'USER': os.environ.get('DJANGO_SCATL_DB_USER', 'dev'),
        'PASSWORD': os.environ.get('DJANGO_SCATL_DB_PASSWORD', 'dev'),
        'HOST': os.environ.get('DJANGO_SCATL_DB_HOST', '172.17.0.2'),
        'PORT': 5432,
    }
}

if IS_GITLAB_CI_TEST:
    DATABASES['default']['USER'] = 'scatl'
    DATABASES['default']['PASSWORD'] = 'scatl'
    DATABASES['default']['HOST'] = 'postgres'

#------------------------------------------------------------------------------
# applications
#------------------------------------------------------------------------------

# noinspection PyUnresolvedReferences
SHUUP_ENABLED_ADDONS_FILE = os.path.join(BASE_DIR, '../testproject/var', 'enabled_addons')

SHUUP_SCATL_TEST_THEME = 'scatl.tests.testproject.theme'

_installed_apps = [
    'attrim',
    'scatl',
    SHUUP_SCATL_TEST_THEME,
]

INSTALLED_APPS = add_enabled_addons(
    addon_filename=SHUUP_ENABLED_ADDONS_FILE,
    apps=INSTALLED_APPS_SHUUP_DEFAULT + _installed_apps,
)


update_globals()

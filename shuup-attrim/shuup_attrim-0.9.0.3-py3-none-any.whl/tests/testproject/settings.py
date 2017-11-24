import os
from shuup.utils.setup import Setup
from shuup.addons import add_enabled_addons
from shuup_workbench.settings.utils import DisableMigrations

from shuup_testutils.settings_base import *


IS_SHUUP_TEST_LOCAL = os.environ.get('IS_SHUUP_TEST_LOCAL') == 'true'

ATTRIM_IS_SKIP_INTEGRATION = os.environ.get('ATTRIM_IS_SKIP_INTEGRATION') == 'true'

#------------------------------------------------------------------------------
# directories
#------------------------------------------------------------------------------

BASE_DIR = os.path.dirname(__file__)
MEDIA_ROOT = os.path.join(BASE_DIR, 'var', 'media')
# noinspection PyUnresolvedReferences
STATIC_ROOT = os.path.join(BASE_DIR, 'var', 'static')

#------------------------------------------------------------------------------
# databases
#------------------------------------------------------------------------------

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'attrim',
        'USER': 'attrim',
        'PASSWORD': 'attrim',
        'HOST': 'postgres',
        'PORT': 5432,
    }
}

if IS_SHUUP_TEST_LOCAL:
    DATABASES['default']['USER'] = os.environ['ATTRIM_DB_USER']
    DATABASES['default']['PASSWORD'] = os.environ['ATTRIM_DB_PASSWORD']
    DATABASES['default']['HOST'] = os.environ['ATTRIM_DB_HOST']

#------------------------------------------------------------------------------
# applications
#------------------------------------------------------------------------------

# noinspection PyUnresolvedReferences
SHUUP_ENABLED_ADDONS_FILE = os.path.join(BASE_DIR, 'var', 'enabled_addons')

installed_attrim_apps = [
    'attrim',
]

INSTALLED_APPS = add_enabled_addons(
    addon_filename=SHUUP_ENABLED_ADDONS_FILE,
    apps=INSTALLED_APPS_SHUUP_DEFAULT + installed_attrim_apps,
)

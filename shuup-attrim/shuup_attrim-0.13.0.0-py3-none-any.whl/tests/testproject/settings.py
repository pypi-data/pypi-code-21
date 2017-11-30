import os
from shuup.utils.setup import Setup
from shuup.addons import add_enabled_addons
from shuup_workbench.settings.utils import DisableMigrations

from shuup_testutils.settings_base import *


#------------------------------------------------------------------------------
# env vars
#------------------------------------------------------------------------------

IS_GITLAB_CI_TEST = os.environ.get('CI_SERVER_NAME') == 'GitLab CI'

IS_SKIP_INTEGRATION = os.environ.get('ATTRIM_IS_SKIP_INTEGRATION') == 'true'

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
        'USER': os.environ.get('DJANGO_ATTRIM_DB_USER', 'dev'),
        'PASSWORD': os.environ.get('DJANGO_ATTRIM_DB_PASSWORD', 'dev'),
        'HOST': os.environ.get('DJANGO_ATTRIM_DB_HOST', '172.17.0.2'),
        'PORT': 5432,
    }
}

if IS_GITLAB_CI_TEST:
    DATABASES['default']['USER'] = 'ci'
    DATABASES['default']['PASSWORD'] = 'ci'
    DATABASES['default']['HOST'] = 'postgres'

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

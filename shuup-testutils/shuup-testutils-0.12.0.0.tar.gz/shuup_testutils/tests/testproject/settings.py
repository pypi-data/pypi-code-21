from shuup.addons import add_enabled_addons

from shuup_testutils.settings_base import *


#------------------------------------------------------------------------------
# directories
#------------------------------------------------------------------------------

BASE_DIR = os.path.dirname(__file__)
MEDIA_ROOT = os.path.join(BASE_DIR, 'var', 'media')
# noinspection PyUnresolvedReferences
STATIC_ROOT = os.path.join(BASE_DIR, 'var', 'static')

#------------------------------------------------------------------------------
# django
#------------------------------------------------------------------------------

# noinspection PyUnresolvedReferences
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite'),
    }
}

#------------------------------------------------------------------------------
# apps and middleware
#------------------------------------------------------------------------------

# noinspection PyUnresolvedReferences
SHUUP_ENABLED_ADDONS_FILE = os.path.join(BASE_DIR, 'var', 'enabled_addons')

INSTALLED_APPS = add_enabled_addons(
    addon_filename=SHUUP_ENABLED_ADDONS_FILE,
    apps=INSTALLED_APPS_SHUUP_DEFAULT,
)


update_globals()

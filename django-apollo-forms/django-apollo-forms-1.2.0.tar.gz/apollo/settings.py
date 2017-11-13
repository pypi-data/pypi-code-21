"""
Settings for Apollo are all namespaced in the APOLLO setting.
For example your project's `settings.py` file might look like this:
APOLLO = {
    'ROOT_PATH': '/'
}
This module provides the `apollo_settings` object, that is used to access
Graphene settings, checking for user settings first, then falling
back to the defaults.
"""
from __future__ import unicode_literals

from django.conf import settings
from django.test.signals import setting_changed

try:
    import importlib  # Available in Python 3.1+
except ImportError:
    from django.utils import importlib  # Will be removed in Django 1.9


# Copied shamelessly from Graphene which copies shamelessly from Django REST Framework

DEFAULTS = {
    'ROOT_PREFIX': '', # the path at which the apollo URL's are mounted. This should be set if the path is anything but the root
    'BUILDER_REQUIRES_IS_STAFF': True, # if True, then usage of the form builder requires is_staff privileges
    'DOWNLOAD_REQUIRES_IS_STAFF': True, # if True, then downloading submissions for a form requires is_staff privileges
    'GRAPHQL_PATH': '/graphql', # location of the icarus themes directory
    'ICARUS_THEMES_URL': '//static.forthepeople.com/engineering/icarus/v1.0-latest/themes', # location of the icarus themes directory
    'SUBMISSION_EMAIL_FROM': None, # email address to send submission notifications from
}


class ApolloSettings(object):
    """
    A settings object, that allows API settings to be accessed as properties.
    For example:
        from apollo.settings import settings
        print(settings.ROOT_PATH)
    Any setting with string import paths will be automatically resolved
    and return the class, rather than the string literal.
    """

    def __init__(self, user_settings=None, defaults=None):
        if user_settings:
            self._user_settings = user_settings
        self.defaults = defaults or DEFAULTS

    @property
    def user_settings(self):
        if not hasattr(self, '_user_settings'):
            self._user_settings = getattr(settings, 'APOLLO', {})
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid Apollo setting: '%s'" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Cache the result
        setattr(self, attr, val)
        return val


apollo_settings = ApolloSettings(None, DEFAULTS)


def reload_apollo_settings(*args, **kwargs):
    global apollo_settings
    setting, value = kwargs['setting'], kwargs['value']
    if setting == 'APOLLO':
        apollo_settings = ApolloSettings(value, DEFAULTS)


setting_changed.connect(reload_apollo_settings)

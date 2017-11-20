from django.conf import settings as _settings

__author__ = 'Michael'

APP_MANAGER_INTERCEPT_UNREGISTERED = False
if hasattr(_settings, 'APP_MANAGER_INTERCEPT_UNREGISTERED'):
    APP_MANAGER_INTERCEPT_UNREGISTERED = _settings.APP_MANAGER_INTERCEPT_UNREGISTERED

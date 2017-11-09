import logging

from django.conf import settings


class RequireNoBugsnagSetting(logging.Filter):
    """ We want to turn off normal email error logging when buggsnag settings are present """
    def filter(self, record):
        return not hasattr(settings, 'BUGSNAG')

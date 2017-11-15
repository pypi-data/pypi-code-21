from django.conf import settings

SETTINGS = {}
try:
    SETTINGS.update(settings.JMBO_SEARCH)
except AttributeError:
    # No overrides
    pass

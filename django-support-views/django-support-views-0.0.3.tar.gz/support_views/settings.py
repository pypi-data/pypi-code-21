
from django.conf import settings as django_settings


SUPPORT_EXTRA_CONTEXT = getattr(django_settings, "SUPPORT_EXTRA_CONTEXT", lambda r: {})

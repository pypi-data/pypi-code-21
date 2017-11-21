from django.conf import settings
from django.utils.translation import ugettext as _
import os


DEBUG = getattr(settings, 'DEBUG')
BASE_DIR = getattr(settings, 'BASE_DIR')
STRING_SINGLE = getattr(settings, 'STRING_SINGLE')
STRING_SHORT = getattr(settings, 'STRING_SHORT')
STRING_MEDIUM = getattr(settings, 'STRING_MEDIUM')
STRING_NORMAL = getattr(settings, 'STRING_NORMAL')
STRING_LONG = getattr(settings, 'STRING_LONG')
STRING_DOUBLE = getattr(settings, 'STRING_DOUBLE')
HOST = getattr(settings, 'HOST')
SUBDOMAINS = getattr(settings, 'SUBDOMAINS')
PROTOCOL = getattr(settings, 'PROTOCOL')
HOSTNAME = getattr(settings, 'HOSTNAME')
WEBSITE_URL = getattr(settings, 'WEBSITE_URL')
STATIC_URL = getattr(settings, 'STATIC_URL')
STATIC_ROOT = getattr(settings, 'STATIC_ROOT')
MEDIA_URL = getattr(settings, 'MEDIA_URL')
MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')
ADMINS = getattr(settings, 'ADMINS', [])

APP = 'OHM2_PUSHES_LIGHT_'

GATEWAY_ONESIGNAL = getattr(settings, APP + 'GATEWAY_ONESIGNAL', (1, "OneSignal"))
GATEWAY_FIREBASE = getattr(settings, APP + 'GATEWAY_FIREBASE', (2, "Firebase"))
DEFAULT_GATEWAY = getattr(settings, APP + 'DEFAULT_GATEWAY', GATEWAY_ONESIGNAL)

GATEWAYS = getattr(settings, APP + 'GATEWAY_FIREBASE', 
	(
		GATEWAY_ONESIGNAL,
		GATEWAY_FIREBASE,
	)
)



ONESIGNAL_ENABLED = getattr(settings, APP + 'ONESIGNAL_ENABLED', "ohm2_pushes_light.gateways.onesignal" in settings.INSTALLED_APPS)
FIREBASE_ENABLED = getattr(settings, APP + 'FIREBASE_ENABLED', "ohm2_pushes_light.gateways.firebase" in settings.INSTALLED_APPS)



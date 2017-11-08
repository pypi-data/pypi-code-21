from django.conf import settings
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

APP = 'OHM2_ACCOUNTS_LIGHT_'

CHECK_PASSWORD_SECURE = getattr(settings, APP + 'CHECK_PASSWORD_SECURE', True)
SIGNUPS_ENABLED = getattr(settings, APP + 'SIGNUPS_ENABLED', True)
ENABLE_EMAIL_LOGIN = getattr(settings, APP + 'ENABLE_EMAIL_LOGIN', True)
UNIQUE_USER_EMAILS = getattr(settings, APP + 'UNIQUE_USER_EMAILS', True)

SIGNUP_PIPELINE = getattr(settings, APP + 'SIGNUP_PIPELINE', (
	'ohm2_accounts_light.pipelines.signup.user_authtoken',
))

LOGIN_PIPELINE = getattr(settings, APP + 'LOGIN_PIPELINE', (
	'ohm2_accounts_light.pipelines.login.default',
))

LOGOUT_PIPELINE = getattr(settings, APP + 'LOGOUT_PIPELINE', (
	'ohm2_accounts_light.pipelines.logout.default',
))

MINIMUM_PASSWORD_RESET_DELAY = getattr(settings, APP + 'MINIMUM_PASSWORD_RESET_DELAY', 10)
PASSWORD_RESET_SEND_ENABLE = getattr(settings, APP + 'PASSWORD_RESET_SEND_ENABLE', True)
PASSWORD_RESET_TEMPLATE_PATH = getattr(settings, APP + 'PASSWORD_RESET_TEMPLATE_PATH', os.path.join( os.path.dirname(os.path.realpath(__file__)), "templates/ohm2_accounts_light/password_reset.html" ))
PASSWORD_RESET_FROM_EMAIL = getattr(settings, APP + 'PASSWORD_RESET_FROM_EMAIL', "no-replay@" + HOSTNAME)
PASSWORD_RESET_SUBJECT = getattr(settings, APP + 'PASSWORD_RESET_SUBJECT', "Password reset")


FACEBOOK_LOGIN = getattr(settings, APP + 'FACEBOOK_LOGIN', False)
FACEBOOK_ME_FIELDS = getattr(settings, APP + 'FACEBOOK_ME_FIELDS', "id,name,email,birthday,gender,relationship_status,picture.type(large)")

GOOGLE_PLUS_LOGIN = getattr(settings, APP + 'GOOGLE_PLUS_LOGIN', False)
GOOGLE_PLUS_PEOPLE_ME_URL = getattr(settings, APP + 'GOOGLE_PLUS_PEOPLE_ME_URL', "https://www.googleapis.com/plus/v1/people/me/")
ENABLE_SOCIAL_LOGIN = FACEBOOK_LOGIN or GOOGLE_PLUS_LOGIN

INCLUDE_PATCHED_URLS = getattr(settings, APP + 'INCLUDE_PATCHED_URLS', False)


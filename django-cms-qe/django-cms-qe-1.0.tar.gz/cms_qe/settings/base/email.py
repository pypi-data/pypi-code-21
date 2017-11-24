"""
Mailing settings, by default app looks for smtp server.
"""

EMAIL_HOST = 'smtp'
EMAIL_PORT = 587

EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''

EMAIL_USE_TLS = True
EMAIL_SUBJECT_PREFIX = ''

DEFAULT_FROM_EMAIL = 'django_cms_qe@localhost'

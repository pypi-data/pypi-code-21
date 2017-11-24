"""
Logging settings with base formatters and handlers.
"""

# Logging
# https://docs.djangoproject.com/en/1.11/topics/logging/

SERVER_EMAIL = 'django_cms_qe@localhost'

ADMINS = (
    ('Michal Hořejšek', 'michal.horejsek@nic.cz'),
)
MANAGERS = ADMINS


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'short': {
            'format': '%(levelname)s [%(filename)s:%(lineno)s] %(message)s',
            'datefmt': '%d/%b/%Y %H:%M:%S'
        },
        'long': {
            'format': '[%(asctime)s] %(levelname)s [%(pathname)s:%(lineno)s] %(message)s',
            'datefmt': '%d/%b/%Y %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'short'
        },
        'logfile': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/tmp/django_cms_qe.log',
            'maxBytes': 5000000,  # 5M
            'backupCount': 0,
            'formatter': 'long',
        },
        'mailadmins': {
            'level': 'WARNING',
            'class': 'django.utils.log.AdminEmailHandler'
        },
    },
    'loggers': {
        'django': {
            'level': 'ERROR',
            'handlers': ['mailadmins'],
            'propagate': True,
        },
        'cms_qe*': {
            'level': 'WARNING',
            'handlers': ['mailadmins'],
            'propagate': True,
        },
        '': {
            'level': 'INFO',
            'handlers': ['console', 'logfile'],
        },
    }
}

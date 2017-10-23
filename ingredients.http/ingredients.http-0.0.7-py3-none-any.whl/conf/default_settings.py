import logging
import os

####################
# CORE             #
####################

DEBUG = True if os.environ.get('PRODUCTION') is None else False

LOGGING_LEVEL = logging.getLevelName(logging.INFO)
LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s][%(name)s][%(levelname)s] %(message)s',
            'datefmt': '%Y-%m-%dT%H:%M:%S%z'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        }
    },
    'loggers': {
        'ingredients_http': {
            'level': LOGGING_LEVEL,
            'handlers': ['console']
        },
        'ingredients_db': {
            'level': LOGGING_LEVEL,
            'handlers': ['console']
        },
        'cherrypy.access': {
            'level': 'INFO',
            'handlers': ['console']
        },
        'cherrypy.error': {
            'level': 'INFO',
            'handlers': ['console']
        },
        'sqlalchemy': {
            'level': 'WARN',
            'handlers': ['console']
        }
    }
}

####################
# DATABASE         #
####################

# Only PostgreSQL is supported
DATABASE_HOST = '127.0.0.1'
DATABASE_PORT = '5432'
DATABASE_USERNAME = 'postgres'
DATABASE_PASSWORD = 'postgres'
DATABASE_DB = 'my_db'
DATABASE_POOL_SIZE = 20


AWS_ACCESS_KEY_ID = ""

AWS_SECRET_ACCESS_KEY = ""

AWS_REGION_NAME = ""

AWS_BUCKET_NAME = ""

AWS_BASE_PATH = "services/modelhub/"

LOG_CONFIG = {
    'version': 1,
    'formatters': {
        'verbose': {'format': "[%(asctime)-15s] [%(levelname)-5s] [%(name)s] %(message)s"},
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'api_model': {
            'handlers': ['console'],
            'level': 'INFO',
        }
    },
}
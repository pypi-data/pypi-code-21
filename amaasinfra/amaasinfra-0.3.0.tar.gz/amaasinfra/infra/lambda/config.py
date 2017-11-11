import os

ENVIRONMENT = 'dev'

if os.environ.get('AWS_DEFAULT_REGION'):
    ENVIRONMENT = os.environ.get('ENVIRONMENT')
import os

from sqlalchemy.engine.url import make_url

####################
# DATABASE         #
####################


if 'CI' in os.environ:
    DATABASE_HOST = '127.0.0.1'
    DATABASE_PORT = '5432'
    DATABASE_USERNAME = 'postgres'
    DATABASE_PASSWORD = ''
    DATABASE_DB = 'test_db'
    DATABASE_POOL_SIZE = 20
else:
    db_url = make_url(os.environ['TEST_DB_URL'])
    DATABASE_HOST = db_url.host
    DATABASE_PORT = db_url.port
    DATABASE_USERNAME = db_url.username
    DATABASE_PASSWORD = db_url.password
    DATABASE_DB = db_url.database
    DATABASE_POOL_SIZE = 20

from mongoframes import *
from pymongo import MongoClient
import pytest

from .frames import Dragon

__all__ = [
    'mongo_client',
    'dragons'
    ]


@pytest.fixture(scope='session')
def mongo_client(request):
    """Connect to the test database"""

    # Connect to mongodb and create a test database
    Frame._client = MongoClient('mongodb://localhost:27017/manhattan_forms')

    def fin():
        # Remove the test database
        Frame._client.drop_database('manhattan_forms')

    request.addfinalizer(fin)

    return Frame._client

@pytest.fixture(scope='function')
def dragons(mongo_client):
    """Create a collection of dragons"""

    Dragon(name='Burt', breed='Fire-drake').insert()
    Dragon(name='Fred', breed='Fire-drake').insert()
    Dragon(name='Albert', breed='Cold-drake').insert()

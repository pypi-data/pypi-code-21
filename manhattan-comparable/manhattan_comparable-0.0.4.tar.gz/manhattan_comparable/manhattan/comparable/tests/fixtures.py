from mongoframes import *
from pymongo import MongoClient
import pytest

from manhattan.comparable.frames import ComparableFrame

from . import Dragon, Lair, User


# Fixtures

@pytest.fixture(scope='function')
def mongo_client(request):
    """Connect to the test database"""

    # Connect to mongodb and create a test database
    db_name = 'manhattan_comparable_test'
    Frame._client = MongoClient(
        'mongodb://localhost:27017/' + db_name)

    def fin():
        # Remove the test database
        Frame._client.drop_database('manhattan_comparable_test')

    request.addfinalizer(fin)

    return Frame._client

@pytest.fixture(scope='function')
def dragon(request):
    """Create a dragon"""

    dungeon = Lair(name='Dungeon')
    dungeon.insert()

    burt = Dragon(
        name='Burt',
        breed='Cold-drake',
        lair=dungeon,
        hobbies=['arson', 'death from above']
        )
    burt.insert()

    return burt

@pytest.fixture(scope='function')
def lair(request):
    """Create a lair"""
    cave = Lair(name='Cave')
    cave.insert()

    return cave

@pytest.fixture(scope='function')
def user(request):
    """Create a user"""
    fred = User(name='Fred')
    fred.insert()

    return fred
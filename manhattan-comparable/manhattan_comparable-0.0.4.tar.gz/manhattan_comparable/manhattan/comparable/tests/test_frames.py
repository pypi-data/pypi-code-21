from datetime import date
import pytest

from manhattan.comparable.change_log import ChangeLogEntry
from manhattan.comparable.frames import ComparableFrame

from . import Dragon, Lair, User

pytest_plugins = ['manhattan.comparable.tests.fixtures']


# Tests

def test_init(mongo_client):
    """Should create a new Dragon instance"""

    # Passing no inital values
    burt = Dragon()
    assert isinstance(burt, Dragon)

    # Check the '_id', 'created' and 'modified' fields have been added by
    # default.
    assert '_id' in burt._fields
    assert 'created' in burt._fields
    assert 'modified' in burt._fields

    # Check the collection name has been set as the class name
    assert burt._collection == 'Dragon'

    # Passing initial values
    burt = Dragon(
        name='Burt',
        breed='Cold-drake'
        )
    assert burt.name == 'Burt'
    assert burt.breed == 'Cold-drake'

def test_comparable(mongo_client, dragon):
    """Should return a dictionary that can be compared"""
    assert dragon.comparable == {
        'breed': 'Cold-drake',
        'hobbies': ['arson', 'death from above'],
        'lair': Lair.by_id(dragon.lair._id),
        'name': 'Burt'
        }

def test_logged_delete(mongo_client, dragon, user):
    """Should delete the document and log the event in the change log"""
    dragon.logged_delete(user)

    # Check the document was deleted
    assert Dragon.by_id(dragon._id) is None

    # Check an entry for the deletion was stored
    entry = ChangeLogEntry.one()
    assert entry.type == 'DELETED'
    assert entry.documents == [dragon._id]
    assert entry.user == user._id

def test_logged_insert(mongo_client, user):
    """
    Should create and insert the document and log the event in the change log.
    """

    burt = Dragon(
        name='Burt',
        breed='Cold-drake'
        )
    burt.logged_insert(user)

    # Check the dragon was created
    assert burt._id is not None

    # Check an entry for the insert was stored
    entry = ChangeLogEntry.one()
    assert entry.type == 'ADDED'
    assert entry.documents == [burt._id]
    assert entry.user == user._id

def test_logged_update(mongo_client, dragon, user):
    """
    Should update the document with the dictionary dat provided and log the
    event in the change log.
    """
    dragon.logged_update(user, {'name': 'Burtress'})

    # Check the dragon was updated
    dragon.reload()
    assert dragon.name == 'Burtress'

    # Check an entry for the update was stored
    entry = ChangeLogEntry.one()
    assert entry.type == 'UPDATED'
    assert entry.documents == [dragon._id]
    assert entry.user == user._id
    assert entry.details == {'updates': {'name': ['Burt', 'Burtress']}}

def test_logged_update_no_update(mongo_client, dragon, user):
    """Should log no event if no comparable change was detected"""
    dragon.logged_update(user, {'name': 'Burt'})

    # Check no entry was created
    entry = ChangeLogEntry.one()
    assert entry is None

def test_compare_safe():
    """
    Should return a value that can safely be compared, by default this method
    simply converts dates to strings.
    """

    today = date.today()

    unsafe = {
        'foo': 'bar',
        'date': today,
        'dates': [today],
        'date_table': {'today': today}
    }

    safe = {
        'foo': 'bar',
        'date': str(today),
        'dates': [str(today)],
        'date_table': {'today': str(today)}
    }

    assert ComparableFrame.compare_safe(unsafe) == safe
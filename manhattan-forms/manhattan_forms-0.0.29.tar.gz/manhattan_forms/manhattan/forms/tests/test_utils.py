from bson.objectid import ObjectId
from mongoframes import Frame
import pytest

from manhattan.forms import utils


def test_sort_by_choices():
    """Add decending sort by options to a list of ascending sort by choices"""
    asc_choices = [
        ('full_name_lower', 'Name'),
        ('role', 'Role')
        ]

    # Check descending choices are added
    choices = utils.sort_by_choices(asc_choices)
    assert choices == [
        ('full_name_lower', 'Name'),
        ('-full_name_lower', 'Name: reverse'),
        ('role', 'Role'),
        ('-role', 'Role: reverse')
        ]

    # Check a custom label can be provided
    choices = utils.sort_by_choices(asc_choices, ' (desc)')
    assert choices == [
        ('full_name_lower', 'Name'),
        ('-full_name_lower', 'Name (desc)'),
        ('role', 'Role'),
        ('-role', 'Role (desc)')
        ]

def test_to_object_id():
    """Coerce a value to an ObjectId"""
    object_id = ObjectId('507f1f77bcf86cd799439011')

    # Check a string is coerced
    assert utils.to_object_id('507f1f77bcf86cd799439011') == object_id

    # Check an ObjectId is coerced
    assert utils.to_object_id(object_id) == object_id

    # Check a ValueError is raised for a value that can't be coerced
    with pytest.raises(ValueError) as exeinfo:
        utils.to_object_id('123')

    # Check that an empty string is returned for an empty string
    assert utils.to_object_id('') == ''

    # Check frame instances are convert to Ids
    class DummyFrame(Frame):

        _fields = {'_id'}

    dummy = DummyFrame({'_id': object_id})
    assert utils.to_object_id(dummy) == object_id

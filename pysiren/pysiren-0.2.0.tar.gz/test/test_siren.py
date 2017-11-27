from pysiren import *
from nose.tools import *


def test_siren_entity_creation():
    entity = SirenEntity('name')

    assert(entity is not None)
    assert(entity.get_class() == 'name')


def test_siren_entity_properties():
    entity = SirenEntity('name')

    assert(entity.get_properties() is None)

    entity.set_properties(None)
    assert(entity.get_properties() is None)

    properties = {'a': 1, 'b': 'c', 'd': [1, 2, 3]}
    entity.set_properties(properties)
    assert(entity.get_properties() == properties)


@raises(SirenEntityError)
def test_siren_entity_properties_error():
    entity = SirenEntity('name')
    entity.set_properties('explode!')

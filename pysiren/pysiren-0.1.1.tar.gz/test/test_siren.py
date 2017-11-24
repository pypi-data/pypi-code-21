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


def test_siren_render():
    entity = SirenEntity(['class1', 'class2'])
    expected = {'class': ['class1', 'class2']}
    assert(entity.render() == expected)


def test_siren_render_full():
    entity = SirenEntity(['className'],
                         title='entityTitle',
                         links=[
                             SirenLink([RelValue.NEXT], "next/link",
                                       title="Link to next",
                                       type=MediaType("application/json"),
                                       classes=["c1", "c2"])
                         ],
                         actions=[
                             SirenAction("add-item",
                                         href="http://api.com/add",
                                         title="Add Item",
                                         method=Method.POST,
                                         type=MediaType('application/x-www-form-urlencoded'),
                                         fields=[
                                             Field("orderNumber", type=FieldType.HIDDEN, value=42),
                                             Field("productCode", type=FieldType.TEXT),
                                             Field("quantity", type=FieldType.NUMBER)
                                         ])
                         ]
    )

    expected = {
        'class': ['className'],
        'title': 'entityTitle',
        'links': [
            {'rel': ["next"], 'href': 'next/link', 'title':'Link to next', 'type': 'application/json', 'class': ['c1', 'c2']}
        ],
        "actions": [
            {
                "name": "add-item",
                "title": "Add Item",
                "method": "POST",
                "href": "http://api.com/add",
                "type": "application/x-www-form-urlencoded",
                "fields": [
                    {"name": "orderNumber", "type": "hidden", "value": 42},
                    {"name": "productCode", "type": "text"},
                    {"name": "quantity", "type": "number"}
                ]
            }
        ],
    }

    result = entity.render()
    assert(expected == result)

from pysiren import *


def test_siren_render():
    entity = SirenEntity(['class1', 'class2'])
    expected = {'class': ['class1', 'class2']}
    assert(entity.render() == expected)


def test_siren_render_full():
    entity = SirenEntity(['className'],
                         title='entityTitle',
                         links=[
                             SirenLink([SirenPredefRelValue.NEXT], "next/link",
                                       title="Link to next",
                                       type=SirenMediaType("application/json"),
                                       classes=["c1", "c2"])
                         ],
                         actions=[
                             SirenAction("add-item",
                                         href="http://api.com/add",
                                         title="Add Item",
                                         method=Method.POST,
                                         type=SirenMediaType('application/x-www-form-urlencoded'),
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

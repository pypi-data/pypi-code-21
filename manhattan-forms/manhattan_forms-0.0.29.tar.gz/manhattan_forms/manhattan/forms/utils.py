from bson.errors import InvalidId as InvalidObjectId
from bson.objectid import ObjectId
from mongoframes import Frame

__all__ = [
    'sort_by_choices',
    'to_object_id'
    ]


def sort_by_choices(choices, label=': reverse'):
    """
    List views typically allow the documents they list to be sorted. The fields
    they can be sorted by are managed through a select field in a form where
    each choice is of the form `({field_name}, {field_label})` (e.g:
    `('full_name_lower', 'Name')`.

    To indicate a descending sort direction we prefix a minus sign to the field
    name (e.g `'-full_name_lower'`) and often postfix something
    (e.g ': reverse') to the label.

    Having to declare both the ascending and descending sort directions for each
    choice can be a little long winded (like this description of the problem)
    and so this function automatically adds descending choices to a list of
    ascending choices you give it, e.g:

    For example:

        sort_by = SelectField(
            'Order',
            choices=sort_by_choices([
                ('full_name_lower', 'Name'),
                ('role', 'Role')
                ]),
            default='full_name_lower'
        )
        print(sort_by.choices)

        ...

        [
            ('full_name_lower', 'Name'),
            ('-full_name_lower', 'Name: reverse'),
            ('role', 'Role'),
            ('-role', 'Role: reverse')
        ]

    Optionally you can specify the label postfixed to descending choices using
    the `label` option.
    """
    return [d for c in choices for d in (c, ('-' + c[0], c[1] + label))]

def to_object_id(value):
    """
    When using a SelectField to select from a list of documents by their
    ObjectIds it would be nice to specify `ObjectId` as the `coerce` argument
    but there are 3 problems with this;

    - an invalid `ObjectId` will raise an `InvalidObjectId` exception not the
      `ValueError` expected by WTForms,
    - if you have an initial empty 'Select...' option and the field is optional
      the empty option wont be accepted as it will fail to coerce.
    - if a Frame instance has been provided rather than an Id then the Id needs
      to be extracted from the instance as it can't be coerced.

    Using `to_object_id` resolves these issues.
    """
    if value is None:
        return None

    if isinstance(value, Frame):
        value = value._id

    try:
        return ObjectId(value)
    except InvalidObjectId:
        if value == '':
            return ''
        raise ValueError('invalid literal for `ObjectId()`')

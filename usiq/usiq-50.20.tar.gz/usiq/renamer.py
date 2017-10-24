import os
from . import parser


def create_filename(tags, pattern):
    fields = parser.get_fields(pattern)
    for field, formatter in fields.items():
        if formatter:
            pattern = pattern.replace(
                '<{}.{}>'.format(field, formatter),
                getattr(tags[field], formatter)())
        else:
            pattern = pattern.replace(
                '<{}>'.format(field),
                tags[field])
    return os.path.expanduser(pattern)

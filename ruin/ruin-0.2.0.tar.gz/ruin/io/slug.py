# -*- coding: utf-8 -*-

from slugify import slugify


def create_unique_slug(item, fields, db_conn, slug_key='slug', separator='-'):
    """
    Generates unique slug

    Checks if slug already exists in DB

    In `fields` must be keys to item or callables
    """

    i = 0
    tokens = []
    for field in fields:
        if callable(field):
            tokens.append(field(item))
        else:
            tokens.append(item[field])

    base_slug = slugify(separator.join(tokens), to_lower=True)
    slug = base_slug
    while db_conn.find_one({slug_key: slug}):
        i += 1
        slug = ''.join([base_slug, separator, str(i)])
    return slug

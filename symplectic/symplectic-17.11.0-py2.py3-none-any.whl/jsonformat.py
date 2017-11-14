"""
Parse JSON files
"""
import functools
import io
import json

from symplectic import posts


def _load(fname):
    with io.open(fname, "r", encoding='utf-8') as filep:
        content = filep.read()
        return json.loads(content)


def _load_with_klass(klass, names):
    return [klass(**_load(name)) for name in names]


# pylint: disable=invalid-name
posts_from_json_files = functools.partial(_load_with_klass, posts.Post)
pages_from_json_files = functools.partial(_load_with_klass, posts.Page)
# pylint: enable=invalid-name

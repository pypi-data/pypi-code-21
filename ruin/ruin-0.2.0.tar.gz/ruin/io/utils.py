# -*- coding: utf-8 -*-

import hashlib
import logging as log
import random
import re
import string

from copy import deepcopy
from sys import exc_info
from traceback import format_exception

from bson.json_util import dumps

from .encoders import MongoJSONEncoder

FIRST_CAP_RE = re.compile('(.)([A-Z][a-z]+)')
ALL_CAP_RE = re.compile('([a-z0-9])([A-Z])')


def document_etag(value, ignore_fields=None):
    if ignore_fields:
        def filter_ignore_fields(doc, fields):
            for field in fields:
                key, _, value = field.partition(".")
                if value:
                    filter_ignore_fields(doc[key], [value])
                elif field in doc:
                    doc.pop(field)
                else:
                    pass

        value_ = deepcopy(value)
        filter_ignore_fields(value_, ignore_fields)
    else:
        value_ = value

    hashish = hashlib.sha1()
    json_encoder = MongoJSONEncoder()
    hashish.update(dumps(value_, sort_keys=True, default=json_encoder.default).encode('utf-8'))
    return hashish.hexdigest()


def camel_to_underscores(stringz0r):
    result = FIRST_CAP_RE.sub(r'\1_\2', stringz0r)
    return ALL_CAP_RE.sub(r'\1_\2', result).lower()


def random_string(length=8, alphabet=None):
    alphabet = alphabet or (string.ascii_letters + string.digits)
    return ''.join(random.choice(alphabet) for x in range(length))


def catch_exception_info():
    (type_exc, value, tbck) = exc_info()
    exc_str = ''.join(format_exception(type_exc, value, tbck))
    del tbck
    log.error(exc_str)
    return exc_str

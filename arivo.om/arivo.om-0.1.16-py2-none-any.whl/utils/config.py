# builtins is python 3.x feature
import __builtin__
import logging
import os

import related
import six


def _save_cast(obj, key, to_type, default):
    try:
        return to_type(obj[key])
    except (ValueError, TypeError, KeyError):
        return default


def int(key, default=0):
    return _save_cast(os.environ, key, __builtin__.int, default)


def float(key, default=0.0):
    return _save_cast(os.environ, key, __builtin__.float, default)


def string(key, default=""):
    assert isinstance(default, six.string_types)
    return os.environ.get(key, default)


def bool(key, default=False):
    assert isinstance(default, __builtin__.bool)
    val = get(key, None)
    if val is None:
        return default
    return val.upper().strip('\'" .,;-_') in ["T", "TRUE", "1", "Y", "YES", "J", "JA"]


def get(key, default=""):
    return os.environ.get(key, default)


def log_level():
    log_levels = {
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
        "WARN": logging.WARNING,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "ERR": logging.ERROR
    }
    return log_levels.get(os.environ.get("LOG_LEVEL", "INFO").upper(), logging.INFO)


def from_yaml(path, cls):
    if not os.path.exists(path):
        return cls()
    with open(path) as f:
        y = f.read().strip()
    d = related.from_yaml(y)
    return related.to_model(cls, d)

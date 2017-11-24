'''
    guide-search
    -----------
    This module provides the interface to elasticsearch
    :copyright: (c) 2017 John Pickerill.
    :license: MIT/X11, see LICENSE for more details.
'''

# -*- coding: utf-8 -*-

from .__about__ import __version__, __title__
from .esearch import Esearch
from .dsl import Dsl
from .exceptions import (    # noqa: F401
    BadRequestError,            # 400
    ResourceNotFoundError,      # 404
    ConflictError,              # 409
    PreconditionError,          # 412
    ServerError,                # 500
    ServiceUnreachableError,    # 503
    UnknownError,               # unexpected htstp response
    ResultParseError,           # es result not in expected form
    CommitError,
    JSONDecodeError,
    ValidationError)

__service_name__ = __title__

__all__ = [ 'Esearch',
            'Dsl',
            'ResourceNotFoundError',
            '__version__']

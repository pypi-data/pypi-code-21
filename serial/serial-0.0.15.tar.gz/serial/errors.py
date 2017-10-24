from __future__ import nested_scopes, generators, division, absolute_import, with_statement, print_function,\
    unicode_literals
from future import standard_library
standard_library.install_aliases()

try:
    import typing
except ImportError as e:
    typing = None

class ValidationError(Exception):

    pass


class VersionError(AttributeError):

    pass

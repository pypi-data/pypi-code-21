"""Exceptions classes used in dataclay."""

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'


class DataclayException(Exception):
    """Base class for exceptions in this module."""
    pass


class ImproperlyConfigured(DataclayException):
    """Raised when the settings are not well-formed."""
    # def __init__(self, msg):
    #     self.msg = msg
    pass


class IdentifierNotFound(DataclayException):
    """Raised when a certain identifier (UUID, name...) has not been found."""
    pass


class InvalidPythonSignature(DataclayException):
    """Raised when trying to use a not recognizable Python-signature."""
    pass

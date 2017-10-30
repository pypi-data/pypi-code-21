"""Module containing all the exceptions included in the pygametemplate module."""
from pygame import error as PygameError  # pylint: disable=unused-import, no-name-in-module


class CaughtFatalException(Exception):
    """Raised by pygametemplate.core.log() when it catches a fatal exception."""

    pass

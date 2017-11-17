# -*- coding: utf-8 -*-
"""Schema interfaces."""

# zope imports
from zope.i18n.interfaces import ILanguageAvailability as \
    IBaseLanguageAvailability
from zope.interface import Interface
from zope.schema import interfaces


class ILanguageAvailability(IBaseLanguageAvailability):
    """A list of available languages."""

    def getAvailableLanguages():
        """Return a sequence of language tags for available languages."""

    def getDefaultLanguage(combined=False):
        """Return the system default language."""

    def getLanguages(combined=False):
        """Return a sequence of Language objects for available languages."""

    def getLanguageListing(combined=False):
        """Return a sequence of language code and language name tuples."""


class II18NField(interfaces.IDict):
    """Marker interface used to identify I18N properties."""


class II18NTextLineField(II18NField):
    """Marker interface used to identify I18N textline properties."""


class II18NTextField(II18NField):
    """Marker interface used to identify I18N text properties."""


class II18NDictReader(Interface):
    """Default value dict reading methods"""

    def __unicode__():
        """Create a unicode representation of the dictionary."""

    def __str__():
        """Create a string representation of the dictionary."""

    def __nonzero__():
        """Return whether the dictionary is considered empty or not."""

    def keys():
        """Get dict keys"""

    def values():
        """Get dict values"""

    def items():
        """Get dict items"""

    def get_for_language(language):
        """Get the value for a specific language using the appropriate default
        if it is a required field.
        """

    def copy():
        """Return an exact copy of the given dict with all associated
        properties."""

    def to_dict():
        """Return a plain dict representation of the object."""

    def to_text():
        """Return a string of all text values appended together."""


class II18NDictWriter(Interface):
    """Default value dict writing methods"""

    def __delitem__(key):
        """Delete specified key from dict"""

    def __setitem__(key, value):
        """Set specified key with specified value"""

    def clear():
        """Remove all dict values"""

    def add(language, value):
        """Add a value for the given language."""

    def remove(language):
        """Remove the value for the given language."""

    def update(*args, **kwargs):
        """Update dict with values from specified dict"""

    def setdefault(key, failobj=None):
        """Get given key from dict or set it with specified value"""

    def pop(key, *args):
        """Remove given key from dict and return its value"""

    def popitem():
        """Pop last item from dict"""


class II18NDict(II18NDictReader, II18NDictWriter):
    """Default value dict marker interface"""

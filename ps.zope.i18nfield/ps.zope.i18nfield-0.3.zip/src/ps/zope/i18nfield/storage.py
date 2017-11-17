# -*- coding: utf-8 -*-
"""Storage components."""

# zope imports
from persistent.dict import PersistentDict
from zope.interface import implementer

# local imports
from ps.zope.i18nfield import (
    interfaces,
    utils,
)

_marker = dict()
KEY_DEFAULT = u'__default_value'


@implementer(interfaces.II18NDict)
class I18NDict(PersistentDict):
    """A custom dictionnary handling a default value."""

    @classmethod
    def from_text(cls, value):
        """Create a new I18nDict from a str or unicode value."""
        klass = cls()
        klass[KEY_DEFAULT] = value
        return klass

    def __init__(self, *args, **kw):
        super(I18NDict, self).__init__()
        self.update(*args, **kw)
        self.default_language = None
        self.required = False

    def __unicode__(self):
        """Return the unicode representation of the dictionary by first trying
        to access the value for the current selected language (i.e. from the
        request). If no value exists for this language and the associated
        schema field is required, try to find the best default fallback value
        available.
        """
        if len(self) == 0:
            return u''
        lang_req = utils.get_language()
        value = self.get_for_language(lang_req)
        if value is None:
            return u''
        return unicode(value)

    def __str__(self):
        """Return the utf-8 encoded respresentation of the dictionary."""
        return unicode(self).encode('utf-8')

    def __nonzero__(self):
        """Return whether the dictionary is considered empty or not."""
        lang_req = utils.get_language()
        return self.get_for_language(lang_req) is not None

    def __hash__(self):
        return hash(str(self))

    def __setitem__(self, key, value):
        """Set a new value, but first doing a validity check."""
        if not value:
            return
        if key != KEY_DEFAULT and key not in utils.available_languages():
            return
        super(I18NDict, self).__setitem__(key, value)

    def get_default_value(self):
        """Returns the best available default value based on the following
        order:
        1. self.default_language
        2. Context/application default (utility)
        3. First non-empty value
        4. None
        """
        result = self.get(self.default_language)
        if not result:
            result = self.get(utils.get_default_language())
            if not result:
                for value in sorted(self.values()):
                    if value:
                        return value

        return result

    def get_for_language(self, language):
        """Get the value for a specific language using the appropriate default
        if it is a required field.
        """
        result = self.get(language, self.get(KEY_DEFAULT))
        if not result and self.required:
            result = self.get_default_value()
        return result

    def add(self, language, value):
        """Add a value for the given language."""
        self[language] = value

    def remove(self, language):
        """Remove the value for the given language."""
        if language in self:
            del self[language]

    def update(self, *args, **kwargs):
        """Update the current dict with either a list of tuples or another
        dictionary."""
        if args:
            if len(args) > 1:
                raise TypeError(
                    'update expected at most 1 arguments, got {0}'.format(
                        len(args)
                    )
                )
            other = dict(args[0])
            for key in other:
                self[key] = other[key]
        for key in kwargs:
            self[key] = kwargs[key]

    def copy(self):
        """Return an exact copy of the given dict with all associated
        properties."""
        result = I18NDict(**self)
        result.default_language = self.default_language
        result.required = self.required
        return result

    def to_dict(self):
        """Return a plain dict representation of the object."""
        return dict(**self)

    def to_text(self):
        """Return a string of all text values appended together."""
        return u' '.join(self.values())

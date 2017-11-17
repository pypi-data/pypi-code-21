# -*- coding: utf-8 -*-
"""Utility definitions for Plone usage."""

# zope imports
from plone import api
from plone.i18n.locales.languages import (
    _languagelist,
    _combinedlanguagelist,
)
from zope.interface import implementer

# local imports
from ps.zope.i18nfield.interfaces import ILanguageAvailability


@implementer(ILanguageAvailability)
class LanguageAvailability(object):
    """A list of available languages."""

    def getAvailableLanguages(self, combined=False):
        """Return a sequence of language tags for available languages."""
        languages = _languagelist.keys()
        if combined:
            languages.extend(_combinedlanguagelist.keys())
        return languages

    def getDefaultLanguage(self):
        """Return the system default language."""
        return api.portal.get_default_language()

    def getLanguages(self, combined=False):
        """Return a sequence of Language objects for available languages."""
        languages = _languagelist.copy()
        if combined:
            languages.update(_combinedlanguagelist.copy())
        return languages

    def getLanguageListing(self, combined=False):
        """Return a sequence of language code and language name tuples."""
        languages = _languagelist.copy()
        if combined:
            languages.update(_combinedlanguagelist.copy())
        return [(code, languages[code][u'name']) for code in languages]

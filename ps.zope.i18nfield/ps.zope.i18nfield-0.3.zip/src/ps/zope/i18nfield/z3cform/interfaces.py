# -*- coding: utf-8 -*-
"""Widget interface definitions."""

# zope imports
from z3c.form.interfaces import IWidget


class II18NWidget(IWidget):
    """I18N base widget."""

    def sorted_languages():
        """Returns a list of the language codes in a sorted order."""

    def languages():
        """Returns a dictionary of language codes with language names."""

    def current():
        """Return the current display language."""

    def default_value():
        """Return the default value if it exists for the current widget."""

    def initWidget(widget, language):
        """Initialize the subwidget for the given language."""

    def updateWidget(widget, language):
        """Update the subwidget for the given language."""

    def getWidget(language):
        """Get the subwidget for the given language."""

    def getValue(language):
        """Get the value for the given language."""

    def hasValue(language):
        """Return whether a value exists for the given language."""


class II18NTextWidget(II18NWidget):
    """I18N text widget."""


class II18NTextAreaWidget(II18NWidget):
    """I18N textarea widget."""

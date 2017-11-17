# -*- coding: utf-8 -*-
"""Data converter."""

# zope imports
from z3c.form.converter import BaseDataConverter
from z3c.form.interfaces import IWidget
from zope.component import adapter

# local imports
from ps.zope.i18nfield.interfaces import II18NField


@adapter(II18NField, IWidget)
class I18NFieldDataConverter(BaseDataConverter):
    """Base data converter for I18N fields."""

    def toWidgetValue(self, value):
        if value is None:
            return {}

        # Return the dict with empty values filtered out for the special
        # cases when being used within the plone.registry.
        return dict([(k, v) for k, v in value.items() if v])

    def toFieldValue(self, value):
        if isinstance(value, basestring):
            return {}
        return dict([(k, v) for k, v in value.items() if v])

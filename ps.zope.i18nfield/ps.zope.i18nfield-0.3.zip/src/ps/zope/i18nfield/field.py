# -*- coding: utf-8 -*-
"""A zope.schema field for inline translations."""

# zope imports
from zope.interface import implementer
from zope.schema import (
    Dict,
    Text,
    TextLine,
)
from zope.schema.interfaces import RequiredMissing

# local imports
from ps.zope.i18nfield import (
    interfaces,
    storage,
)


@implementer(interfaces.II18NField)
class I18NField(Dict):
    """Base class for I18n schema fields

    A I18n field is a mapping object for which keys are languages and values
    are effective values of the given attribute. Selected values can be
    returned selectively (for editing), or automatically (to be displayed
    in an HTML page) based on user's browser's language settings.
    """

    def __init__(self, default_language=None, key_type=None, value_type=None,
                 **kw):
        super(I18NField, self).__init__(
            key_type=TextLine(),
            value_type=value_type,
            **kw
        )
        self._default_language = default_language

    def _validate(self, value):
        if isinstance(value, storage.I18NDict):
            value = value.to_dict()
        super(I18NField, self)._validate(value)
        if self.required:
            if not value:
                raise RequiredMissing
            for lang in value.values():
                if lang:
                    return
            raise RequiredMissing


@implementer(interfaces.II18NTextLineField)
class I18NTextLine(I18NField):
    """Schema field used to define an I18n textline property"""

    def __init__(self, key_type=None, value_type=None, value_constraint=None,
                 value_min_length=0, value_max_length=None, **kw):
        super(I18NTextLine, self).__init__(
            value_type=TextLine(
                constraint=value_constraint,
                min_length=value_min_length,
                max_length=value_max_length,
                required=False
            ),
            **kw
        )


@implementer(interfaces.II18NTextField)
class I18NText(I18NField):
    """Schema field used to define an I18n text property"""

    def __init__(self, key_type=None, value_type=None, value_constraint=None,
                 value_min_length=0, value_max_length=None, **kw):
        super(I18NText, self).__init__(
            value_type=Text(
                constraint=value_constraint,
                min_length=value_min_length,
                max_length=value_max_length,
                required=False
            ),
            **kw
        )

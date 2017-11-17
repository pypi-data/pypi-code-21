# -*- coding: utf-8 -*-
"""Adapter for plone.registry."""

# zope imports
from plone.registry.field import (
    DisallowedProperty,
    InterfaceConstrainedProperty,
    StubbornProperty,
    PersistentField,
)
from plone.registry.interfaces import IPersistentField
from zope.component import adapter
from zope.interface import implementer

# local imports
from ps.zope.i18nfield.field import I18NField
from ps.zope.i18nfield.interfaces import II18NField


TRACE = 'The property `{0}` cannot be adapted to `{1}`.'


class I18NFieldPersistent(PersistentField, I18NField):
    key_type = InterfaceConstrainedProperty('key_type', IPersistentField)
    value_type = InterfaceConstrainedProperty('value_type', IPersistentField)


@implementer(IPersistentField)
@adapter(II18NField)
def i18n_persistent_field_adapter(context):
    """Special handling for I18NField fields."""

    if IPersistentField.providedBy(context):
        return context

    ignored = list(DisallowedProperty.uses + StubbornProperty.uses)
    constrained = list(InterfaceConstrainedProperty.uses)
    instance = I18NFieldPersistent.__new__(I18NFieldPersistent)

    context_dict = dict([
        (k, v) for k, v in context.__dict__.items() if k not in ignored
    ])

    for k, iface in constrained:
        v = context_dict.get(k, None)
        if v is not None and v != context.missing_value:
            v = iface(v, None)
            if v is None:
                __traceback_info__ = TRACE.format(k, iface.__identifier__)
                return None
            context_dict[k] = v

    instance.__dict__.update(context_dict)
    return instance

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Interfaces describing the events and fields this package uses.

Also utility functions.
"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import schema
from zope import interface

from zope.schema import interfaces as sch_interfaces

class IBeforeSchemaFieldAssignedEvent(interface.Interface):
    """
    An event sent when certain schema fields will be assigning
    an object to a property of another object.

    The interface :class:`.IBeforeObjectAssignedEvent` is a sub-interface
    of this one.
    """
    object = interface.Attribute(u"The object that is going to be assigned. Subscribers may modify this")

    name = interface.Attribute(u"The name of the attribute under which the object will be assigned.")

    context = interface.Attribute(u"The context object where the object will be assigned to.")

# Make this a base of the zope interface so our handlers
# are compatible
sch_interfaces.IBeforeObjectAssignedEvent.__bases__ = (IBeforeSchemaFieldAssignedEvent,)

@interface.implementer(IBeforeSchemaFieldAssignedEvent)
class BeforeSchemaFieldAssignedEvent(object):

    def __init__(self, obj, name, context):
        self.object = obj
        self.name = name
        self.context = context

class IBeforeTextAssignedEvent(IBeforeSchemaFieldAssignedEvent):
    """
    Event for assigning text.
    """

    object = schema.Text(title=u"The text being assigned.")

class IBeforeTextLineAssignedEvent(IBeforeTextAssignedEvent):  # ITextLine extends IText
    """
    Event for assigning text lines.
    """

    object = schema.TextLine(title=u"The text being assigned.")

class IBeforeContainerAssignedEvent(IBeforeSchemaFieldAssignedEvent):
    """
    Event for assigning containers (__contains__).
    """

class IBeforeIterableAssignedEvent(IBeforeContainerAssignedEvent):
    """
    Event for assigning iterables.
    """

class IBeforeCollectionAssignedEvent(IBeforeIterableAssignedEvent):
    """
    Event for assigning collections.
    """

    object = interface.Attribute(u"The collection being assigned. May or may not be mutable.")

class IBeforeSetAssignedEvent(IBeforeCollectionAssignedEvent):
    """
    Event for assigning sets.
    """

class IBeforeSequenceAssignedEvent(IBeforeCollectionAssignedEvent):
    """
    Event for assigning sequences.
    """

    object = interface.Attribute(u"The sequence being assigned. May or may not be mutable.")

class IBeforeDictAssignedEvent(IBeforeIterableAssignedEvent):
    """
    Event for assigning dicts.
    """

# The hierarchy is IContainer > IIterable > ICollection > ISequence > [ITuple, IList]
# Also:         IContainer > IIterable > IDict
# Also:         IContainer > IIterable > ISet

@interface.implementer(IBeforeTextAssignedEvent)
class BeforeTextAssignedEvent(BeforeSchemaFieldAssignedEvent):
    pass

@interface.implementer(IBeforeTextLineAssignedEvent)
class BeforeTextLineAssignedEvent(BeforeTextAssignedEvent):
    pass


@interface.implementer(IBeforeCollectionAssignedEvent)
class BeforeCollectionAssignedEvent(BeforeSchemaFieldAssignedEvent):
    object = None

@interface.implementer(IBeforeSequenceAssignedEvent)
class BeforeSequenceAssignedEvent(BeforeCollectionAssignedEvent):
    pass

@interface.implementer(IBeforeSetAssignedEvent)
class BeforeSetAssignedEvent(BeforeCollectionAssignedEvent):
    pass

@interface.implementer(IBeforeDictAssignedEvent)
class BeforeDictAssignedEvent(BeforeSchemaFieldAssignedEvent):
    pass

from zope.schema._field import BeforeObjectAssignedEvent
BeforeObjectAssignedEvent = BeforeObjectAssignedEvent

class InvalidValue(sch_interfaces.InvalidValue):
    """
    Adds a field specifically to carry the value that is invalid.
    """
    value = None

    def __init__(self, *args, **kwargs):
        super(InvalidValue, self).__init__(*args)
        if 'value' in kwargs:
            self.value = kwargs['value']
        if 'field' in kwargs:
            self.field = kwargs['field']

# And we monkey patch it in to InvalidValue as well
if not hasattr(sch_interfaces.InvalidValue, 'value'):
    setattr(sch_interfaces.InvalidValue, 'value', None)

# And give all validation errors a 'field'
if not hasattr(sch_interfaces.ValidationError, 'field'):
    setattr(sch_interfaces.ValidationError, 'field', None)

class IFromObject(interface.Interface):
    """
    Something that can convert one type of object to another,
    following validation rules (see :class:`zope.schema.interfaces.IFromUnicode`)
    """

    def fromObject(obj):
        """
        Attempt to convert the object to the required type following
        the rules of this object. Raises a TypeError or :class:`zope.schema.interfaces.ValidationError`
        if this isn't possible.
        """

class IVariant(sch_interfaces.IField, IFromObject):
    """
    Similar to :class:`zope.schema.interfaces.IObject`, but
    representing one of several different types.
    """

class IListOrTuple(sch_interfaces.IList):
    pass

def find_most_derived_interface(ext_self, iface_upper_bound, possibilities=None):
    """
    Search for the most derived version of the interface `iface_upper_bound`
    implemented by `ext_self` and return that. Always returns at least `iface_upper_bound`

    :keyword possibilities: An iterable of schemas to consider. If not given,
        all the interfaces provided by ``ext_self`` will be considered.
    """
    if possibilities is None:
        possibilities = interface.providedBy(ext_self)
    _iface = iface_upper_bound
    for iface in possibilities:
        if iface.isOrExtends(_iface):
            _iface = iface
    return _iface

try:
    from dm.zope.schema.interfaces import ISchemaConfigured as _ISchemaConfigured
except ImportError:
    _ISchemaConfigured = interface.Interface

class ISchemaConfigured(_ISchemaConfigured):
    """
    marker interface for ``SchemaConfigured`` classes.

    Used to facilitate the registration of forms and views.
    """

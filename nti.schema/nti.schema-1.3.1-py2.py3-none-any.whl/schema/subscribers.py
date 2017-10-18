#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Event handlers.

"""

from __future__ import print_function, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component

from zope.component import handle

from nti.schema.interfaces import IBeforeSchemaFieldAssignedEvent

@component.adapter(IBeforeSchemaFieldAssignedEvent)
def before_object_assigned_event_dispatcher(event):
    """
    Listens for :mod:`zope.schema` fields to fire :class:`~.IBeforeSchemaFieldAssignedEvent`,
    and re-dispatches these events based on the value being assigned, the object being assigned to,
    and of course the event (note that :class:`~zope.schema.interfaces.IBeforeObjectAssignedEvent` is a
    sub-interface of :class:`.~IBeforeSchemaFieldAssignedEvent`).

    This is analogous to :func:`zope.component.event.objectEventNotify`
    """
    handle(event.object, event.context, event)

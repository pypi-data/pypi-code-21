""" Custom events
"""
import logging
from zope.interface import implementer
from zope.lifecycleevent import ObjectModifiedEvent
from zope.component.interfaces import ObjectEvent
from eea.relations.events.interfaces import IObjectInitializedEvent
from eea.relations.events.interfaces import IRelatedItemsWorkflowStateChanged
from eea.relations.events.interfaces import IForwardRelatedItemsWSC
from eea.relations.events.interfaces import IBackwardRelatedItemsWSC
logger = logging.getLogger("eea.relations")


@implementer(IObjectInitializedEvent)
class ObjectInitializedEvent(ObjectModifiedEvent):
    """ An object is being initialised, i.e. populated for the first time
    """


@implementer(IRelatedItemsWorkflowStateChanged)
class RelatedItemsWorkflowStateChanged(ObjectEvent):
    """ Related Items Workflow State Changed
    """


@implementer(IForwardRelatedItemsWSC)
class ForwardRelatedItemsWorkflowStateChanged(
        RelatedItemsWorkflowStateChanged):
    """ Related Items Workflow State Changed
    """


@implementer(IBackwardRelatedItemsWSC)
class BackwardRelatedItemsWorkflowStateChanged(
        RelatedItemsWorkflowStateChanged):
    """ Related Items Workflow State Changed
    """

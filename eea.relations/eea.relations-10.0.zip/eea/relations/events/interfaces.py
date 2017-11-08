""" Events
"""
from zope.component.interfaces import IObjectEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent


class IObjectInitializedEvent(IObjectModifiedEvent):
    """An object is being initialised, i.e. populated for the first time
    """


class IRelatedItemsWorkflowStateChanged(IObjectEvent):
    """ Base Event Interface for all Related Items Workflow State Changed events
    """


class IForwardRelatedItemsWSC(IRelatedItemsWorkflowStateChanged):
    """ Forward Related Items Interface
    """


class IBackwardRelatedItemsWSC(IRelatedItemsWorkflowStateChanged):
    """ Backward Releated Items Interface
    """

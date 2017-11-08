""" Async jobs
"""
import logging
import urlparse
from zope import event
from zope.component import queryAdapter
from plone import api
from eea.relations.events import ForwardRelatedItemsWorkflowStateChanged
from eea.relations.events import BackwardRelatedItemsWorkflowStateChanged
from eea.relations.rules.interfaces import IContextWrapper
logger = logging.getLogger('eea.relations')


def forward_transition_change(obj, transition, portal_url=''):
    """ Forward workflow state changed related items
    """
    relatedItems = obj.getRelatedItems()
    if not relatedItems:
        return

    succeeded = set()
    failed = set()
    for item in relatedItems:
        url = item.absolute_url()
        if not url.startswith('http'):
            url = urlparse.urljoin(portal_url, url)
        try:
            api.content.transition(obj=item, transition=transition)
        except Exception, err:
            logger.debug("%s: %s", item.absolute_url(), err)
            failed.add(url)
        else:
            succeeded.add(url)

    if not (succeeded or failed):
        return

    wrapper = queryAdapter(obj, IContextWrapper)
    if wrapper is not None:
        url = obj.absolute_url()
        if not url.startswith('http'):
            url = urlparse.urljoin(portal_url, url)
        obj = wrapper(
            related_items_changed=succeeded,
            related_items_unchanged=failed,
            related_items_transition=transition,
            related_items_url=url
        )

    event.notify(ForwardRelatedItemsWorkflowStateChanged(obj))


def backward_transition_change(obj, transition, portal_url=None):
    """ Backward workflow state changed related items
    """
    backRefs = obj.getBRefs()
    if not backRefs:
        return

    succeeded = set()
    failed = set()
    for item in backRefs:
        url = item.absolute_url()
        if not url.startswith('http'):
            url = urlparse.urljoin(portal_url, url)
        try:
            api.content.transition(obj=item, transition=transition)
        except Exception, err:
            logger.debug("%s: %s", item.absolute_url(), err)
            failed.add(url)
        else:
            succeeded.add(url)

    if not (succeeded or failed):
        return

    wrapper = queryAdapter(obj, IContextWrapper)
    if wrapper is not None:
        url = obj.absolute_url()
        if not url.startswith('http'):
            url = urlparse.urljoin(portal_url, url)
        obj = wrapper(
            related_items_changed=succeeded,
            related_items_unchanged=failed,
            related_items_transition=transition,
            related_items_url=url
        )

    event.notify(BackwardRelatedItemsWorkflowStateChanged(obj))

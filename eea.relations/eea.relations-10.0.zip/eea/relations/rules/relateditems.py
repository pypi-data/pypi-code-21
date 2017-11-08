""" Related items workflow state changed
"""
import logging

from zope.component import ComponentLookupError
from zope.component import adapter
from zope.component import queryUtility
from zope.component.hooks import getSite
from zope.formlib import form
from zope.interface import implementer, Interface
from OFS.SimpleItem import SimpleItem

from plone.app.contentrules.browser.formhelper import AddForm, EditForm
from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData

from eea.relations.config import EEAMessageFactory as _
from eea.relations.async import IAsyncService
from eea.relations.rules.interfaces import IRelatedItemsAction
from eea.relations.rules.async import forward_transition_change
from eea.relations.rules.async import backward_transition_change

logger = logging.getLogger('eea.relations')


@implementer(IExecutable)
@adapter(Interface, IRelatedItemsAction, Interface)
class RelatedItemsActionExecutor(object):
    """The executor for this action.
    """
    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def forward(self):
        """ Handle related items
        """
        if not self.element.related_items:
            return

        portal_url = getSite().absolute_url()
        if not self.element.asynchronous:
            return forward_transition_change(
                self.event.object,
                self.element.transition,
                portal_url
            )
        async_service = queryUtility(IAsyncService)
        try:
            async_queue = async_service.getQueues()['']
            async_service.queueJobInQueue(
                async_queue, ('relations',),
                forward_transition_change,
                self.event.object,
                self.element.transition,
                portal_url
            )
        except (AttributeError, ComponentLookupError):
            return forward_transition_change(
                self.event.object,
                self.element.transition,
                portal_url
            )

    def backward(self):
        """ Handle back refs
        """
        portal_url = getSite().absolute_url()
        if not self.element.backward_related_items:
            return
        if not self.element.asynchronous:
            return backward_transition_change(
                self.event.object,
                self.element.transition,
                portal_url
            )
        async_service = queryUtility(IAsyncService)
        try:
            async_queue = async_service.getQueues()['']
            async_service.queueJobInQueue(
                async_queue, ('relations',),
                backward_transition_change,
                self.event.object,
                self.element.transition,
                portal_url
            )
        except (AttributeError, ComponentLookupError):
            return backward_transition_change(
                self.event.object,
                self.element.transition,
                portal_url
            )

    def __call__(self):
        self.forward()
        self.backward()


@implementer(IRelatedItemsAction, IRuleElementData)
class RelatedItemsAction(SimpleItem):
    """ The actual persistent implementation of the action element.
    """

    transition = u""
    related_items = False
    backward_related_items = False
    asynchronous = False
    element = "eea.relations.workflow"

    @property
    def summary(self):
        """ Need to access the content rule with the related items action.
        """
        return _(
            u"Execute transition ${transition}",
            mapping=dict(transition=self.transition)
        )


class RelatedItemsAddForm(AddForm):
    """
    An add form for the related items action
    """
    form_fields = form.FormFields(IRelatedItemsAction)
    label = _(u"Add Related Items Action")
    description = _(u"Change workflow state for related items.")
    form_name = _(u"Configure element")

    def create(self, data):
        """ Create action
        """
        action = RelatedItemsAction()
        form.applyChanges(action, self.form_fields, data)
        return action


class RelatedItemsEditForm(EditForm):
    """
    An add form for the related items action
    """
    form_fields = form.FormFields(IRelatedItemsAction)
    label = _(u"Add Related Items Action")
    description = _(u"Change workflow state for related items.")
    form_name = _(u"Configure element")

""" Browser edit controllers
"""
import logging
from zope.component import queryAdapter, getMultiAdapter

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

from eea.faceted.inheritance.interfaces import IHeritorAccessor
from eea.faceted.inheritance.interfaces import IFacetedHeritor

logger = logging.getLogger('eea.faceted.inheritance.browser.edit')

class EditForm(BrowserView):
    """ Faceted heritor edit
    """
    def _redirect(self, msg='', to='configure_faceted.html'):
        """ Return or redirect
        """
        if not to:
            return msg

        if not self.request:
            return msg

        if msg:
            IStatusMessage(self.request).addStatusMessage(
                str(msg), type='info')
        self.request.response.redirect(to)
        return msg

    def update(self, **kwargs):
        """ Update
        """
        if getattr(self.request, 'form', None):
            kwargs.update(self.request.form)

        handler = queryAdapter(self.context, IHeritorAccessor)
        if not handler:
            logger.warn('No IHeritorAccessor adapter found for %s',
                        self.context.absolute_url())
            return self._redirect('An error occured')

        ancestor = kwargs.get('ancestor', '')
        handler.ancestor = ancestor
        return self._redirect('Changes saved.')

    def breadcrumbs(self, brain):
        """ Return breadcrumbs for ancestor
        """
        ancestor = brain.getObject()
        view = getMultiAdapter((ancestor, self.request),
                               name=u'breadcrumbs_view')
        return view.breadcrumbs()

    @property
    def ancestors(self):
        """ Possible ancestors
        """
        ctool = getToolByName(self.context, 'portal_catalog')

        brains = ctool(
            object_provides=('eea.facetednavigation'
                             '.subtypes.interfaces.IFacetedNavigable'))
        for brain in brains:
            if IFacetedHeritor.providedBy(brain.getObject()):
                continue
            yield brain

    @property
    def ancestor(self):
        """ Current set ancestor path
        """
        handler = queryAdapter(self.context, IHeritorAccessor)
        if not handler:
            logger.warn('No IHeritorAccessor adapter found for %s',
                        self.context.absolute_url())
            return ''

        return handler.ancestor

""" Discover view controllers
"""
from zope.interface import implements
from zope.component import queryAdapter
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from eea.relations.interfaces import IAutoRelations
from eea.relations.discover.interfaces import IBrowserView
from AccessControl import Unauthorized


class View(BrowserView):
    """ Display auto discovered relations
    """
    implements(IBrowserView)

    def checkPermission(self, brains):
        """ Check document permission
        """
        mtool = getToolByName(self.context, 'portal_membership')
        for brain in brains:
            getObject = getattr(brain, 'getObject', None)
            if getObject:
                try:
                    brain = brain.getObject()
                except Unauthorized:
                    continue
            if mtool.checkPermission('View', brain):
                yield brain

    def generatorTabs(self, tupleResult):
        """ Return a generator from the tuple result which is returned in the
        form of string name + object list
        """
        for tab, brains in tupleResult:
            brains = [b for b in self.checkPermission(brains)]
            if not brains:
                continue
            yield tab, brains

    @property
    def tabs(self):
        """ Return brains
        """
        explorer = queryAdapter(self.context, IAutoRelations)
        # if query adapter doesn't return a match then return an empty list
        if not explorer:
            return []
        explorer = explorer()
        # if adapter returns an empty value then return an empty list as well
        if not explorer:
            return []
        return self.generatorTabs(explorer)

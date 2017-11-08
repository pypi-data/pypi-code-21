""" Faceted criteria
"""
from zope.interface import implements
from zope.component import queryAdapter, getUtility

from eea.faceted.inheritance.criteria.interfaces import ICriteria
from eea.faceted.inheritance.criteria.interfaces import IHeritorAccessor
from eea.facetednavigation.widgets.storage import Criterion
from eea.facetednavigation.interfaces import IWidgetsInfo

from Products.CMFCore.utils import getToolByName

class Criteria(object):
    """ Overrides default facetednavigation functionality
    """
    implements(ICriteria)

    def _ancestor(self, context):
        """ Get ancestor
        """
        handler = queryAdapter(context, IHeritorAccessor)
        path = handler.ancestor
        ctool = getToolByName(context, 'portal_catalog')
        brains = ctool(path={'query': path, 'depth': 0})
        for brain in brains:
            return brain.getObject()
        return None

    def __init__(self, context):
        self.ancestor = self._ancestor(context)
        self.context = self.ancestor or context
        self.adapter = queryAdapter(self.ancestor, ICriteria)
    #
    # Getters
    #
    @property
    def criteria(self):
        """ Get faceted criteria from ancestor
        """
        if not self.ancestor:
            return [
                Criterion(widget='path', index='path',
                          hidden=True, default=self.context.absolute_url(1)),
            ]
        return ICriteria(self.ancestor).criteria

    def newid(self):
        """ Faceted criterion new id
        """
        if not self.adapter:
            return ''
        return self.adapter.newid()

    def get(self, key, default=None):
        """ Get faceted criterion by id from ancestor
        """
        for cid, cvalue in self.items():
            if key == cid:
                return cvalue
        return default

    def keys(self):
        """ Faceted criteria keys from ancestor
        """
        return [criterion.getId() for criterion in self.criteria]

    def values(self):
        """ Faceted criteria values from ancestor
        """
        return [criterion for criterion in self.criteria]

    def items(self):
        """ Faceted criteria items from ancestor
        """
        return [(criterion.getId(), criterion) for criterion in self.criteria]
    #
    # Setters
    #
    def add(self, *args, **kwargs):
        """
        As this is a read-only proxy to a faceted navigable object
        adding widgets is forbidden
        """
        return

    def delete(self, cid):
        """
        As this is a read-only proxy to a faceted navigable object
        deleting widgets is forbidden
        """
        return

    def edit(self, *args, **kwargs):
        """
        As this is a read-only proxy to a faceted navigable object
        editing widgets is forbidden
        """
        return
    #
    # Position
    #
    def up(self, cid):
        """
        As this is a read-only proxy to a faceted navigable object
        moving widgets is forbidden
        """
        return

    def down(self, cid):
        """
        As this is a read-only proxy to a faceted navigable object
        moving widgets is forbidden
        """
        return

    def position(self, **kwargs):
        """
        As this is a read-only proxy to a faceted navigable object
        moving widgets is forbidden
        """
        return
    #
    # Utils
    #
    def widget(self, wid=None, cid=None):
        """ Faceted widget from ancestor
        """
        if not self.adapter:
            return getUtility(IWidgetsInfo).widgets.get('path', None)
        return self.adapter.widget(wid, cid)

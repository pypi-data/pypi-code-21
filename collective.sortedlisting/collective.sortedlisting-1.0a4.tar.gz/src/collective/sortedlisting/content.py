# -*- coding: utf-8 -*-
from collective.sortedlisting.behavior import SortableCollectionBehavior
from collective.sortedlisting.interfaces import ISortableCollection
from plone.app.contenttypes.content import Collection
from Products.CMFPlone.interfaces.syndication import ISyndicatable
from zope.interface import implementer


@implementer(ISortableCollection, ISyndicatable)
class SortableCollection(Collection):
    """ Content type sortable collection """

    def results(self, **kwargs):
        return SortableCollectionBehavior(self).results(**kwargs)

# EOF

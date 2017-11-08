# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from collective.sortedlisting.behavior import SortableCollectionBehavior
from plone.app.contenttypes.browser.collection import CollectionView


class SortableCollectionView(CollectionView):

    @property
    def collection_behavior(self):
        return SortableCollectionBehavior(aq_inner(self.context))

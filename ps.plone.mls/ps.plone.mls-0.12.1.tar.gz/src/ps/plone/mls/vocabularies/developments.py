# -*- coding: utf-8 -*-
"""Vocabularies for development projects."""

# zope imports
from plone import api
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

# local imports
from ps.plone.mls import _
from ps.plone.mls.interfaces import IDevelopmentCollection


@implementer(IVocabularyFactory)
class AvailableDevelopmentCollections(object):
    """Vocabulary which returns all available development collections."""

    def __call__(self, context):
        brains = api.content.find(
            object_provides=IDevelopmentCollection,
            sort_on='sortable_title',
        )
        items = []
        for brain in brains:
            title = '{0} ({1})'.format(brain.Title, brain.getPath())
            items.append(SimpleTerm(brain.UID, brain.UID, title))
        return SimpleVocabulary(items)

AvailableDevelopmentCollectionsFactory = AvailableDevelopmentCollections()


@implementer(IVocabularyFactory)
class SortOptionsVocabulary(object):
    """Return list of sort options for a development collection."""

    def __call__(self, context):
        items = []
        items.append(SimpleTerm('created', _(u'Creation Date')))
        items.append(SimpleTerm('sortable_title', _(u'Title')))
        return SimpleVocabulary(items)

SortOptionsVocabularyFactory = SortOptionsVocabulary()

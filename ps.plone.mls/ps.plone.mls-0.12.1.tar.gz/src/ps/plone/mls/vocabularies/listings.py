# -*- coding: utf-8 -*-
"""Vocabularies for listings."""

# zope imports
from plone import api
from plone.mls.listing.browser.listing_search import IListingSearch
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary


MIN_BEDROOM_VALUES = [
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5+'),
]


@implementer(IVocabularyFactory)
class AvailableListingSearches(object):
    """Vocabulary which returns all available listing searches."""

    def __call__(self, context):
        brains = api.content.find(
            object_provides=IListingSearch,
            sort_on='sortable_title',
        )
        items = []
        for brain in brains:
            title = '{0} ({1})'.format(brain.Title, brain.getPath())
            items.append(SimpleTerm(brain.UID, brain.UID, title))
        return SimpleVocabulary(items)

AvailableListingSearchesFactory = AvailableListingSearches()


@implementer(IVocabularyFactory)
class MinBedroomsVocabulary(object):
    """Vocabulary which returns the values for the min bedrooms field."""

    def __call__(self, context):
        items = []
        for item in MIN_BEDROOM_VALUES:
            items.append(SimpleTerm(item[0], item[0], item[1]))
        return SimpleVocabulary(items)

MinBedroomsVocabularyFactory = MinBedroomsVocabulary()

# -*- coding: utf-8 -*-
from collective.sortedlisting import _
from collective.sortedlisting.widget import SortableQueryStringFieldWidget
from plone.app.contenttypes.behaviors.collection import Collection
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.batching import Batch
from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel import model
from plone.z3cform.textlines import TextLinesFieldWidget
from zope import schema
from zope.component import adapter
from zope.interface import implementer_only
from zope.interface import provider


# we need to inherit from model.Schema here directly
# otherwise this gives some weird overlapping with the
# ICollection interface
@provider(IFormFieldProvider)
class ISortableCollectionBehavior(model.Schema):

    query = schema.List(
        title=_(u'Search terms'),
        description=_(u'Define the search terms for the items you want '
                      u'to list by choosing what to match on. '
                      u'The list of results will be dynamically updated'),
        value_type=schema.Dict(value_type=schema.Field(),
                               key_type=schema.TextLine()),
        required=False,
        missing_value=''
    )
    # override QueryString widget with our sortable version
    form.widget('query',
                SortableQueryStringFieldWidget,
                wrapper_css_class='sortableCollection-query')

    sort_on = schema.TextLine(
        title=_(u'label_sort_on', default=u'Sort on'),
        description=_(u'Sort the collection on this index'),
        required=False,
    )

    sort_reversed = schema.Bool(
        title=_(u'label_sort_reversed', default=u'Reversed order'),
        description=_(u'Sort the results in reversed order'),
        required=False,
    )

    limit = schema.Int(
        title=_(u'Limit'),
        description=_(u'Limit Search Results'),
        required=False,
        default=1000,
        min=1,
    )

    item_count = schema.Int(
        title=_(u'label_item_count', default=u'Item count'),
        description=_(u'Number of items that will show up in one batch.'),
        required=False,
        default=30,
        min=1,
    )

    customViewFields = schema.List(
        title=_(u'Table Columns'),
        description=_(u'Select which fields to display when '
                      u"'Tabular view' is selected in the display menu."),
        default=['Title', 'Creator', 'Type', 'ModificationDate'],
        value_type=schema.Choice(
            vocabulary='plone.app.contenttypes.metadatafields'),
        required=False,
    )

    # we need an additional field to store the sorting
    # as UIDs of the found objects (brains)
    sorting = schema.List(
        title=_(u'Sorting'),
        description=_(u'Widget specific sorting of the search results'),
        default=[],
        missing_value=[],
        value_type=schema.TextLine(),
        required=False,
    )
    # We have to set the widget to update the widget-settings
    form.widget('sorting',
                TextLinesFieldWidget,
                wrapper_css_class='sortableCollection-sorting')


@implementer_only(ISortableCollectionBehavior)
@adapter(IDexterityContent)
class SortableCollectionBehavior(Collection):
    """ """

    def results(self, batch=True, b_start=0, b_size=None,
                sort_on=None, limit=None, brains=False,
                custom_query=None):
        results = super(SortableCollectionBehavior, self).results(
            batch, b_start, b_size, sort_on, limit, brains, custom_query)
        # apply the custom sorting to the resultset according to
        # our sorting list
        positions = {j: i for i, j in enumerate(self.sorting)}
        results = sorted(
            results, key=lambda item: positions.get(item.uuid(), 999))
        if batch:
            if not b_size:
                b_size = self.item_count
            results = Batch(results, b_size, start=b_start)
        return results

    # store and access sorting list from our context (ie. SortableCollection)

    @property
    def sorting(self):
        return getattr(self.context, 'sorting', [])

    @sorting.setter
    def sorting(self, value):
        self.context.sorting = value

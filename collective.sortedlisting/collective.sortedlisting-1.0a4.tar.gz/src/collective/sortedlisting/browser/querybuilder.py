# -*- coding: utf-8 -*-
from plone.app.contentlisting.interfaces import IContentListing
from plone.app.querystring.querybuilder import QueryBuilder as BaseQueryBilder
from plone.batching import Batch
from zope.component import getMultiAdapter


class QueryBuilder(BaseQueryBilder):
    """ This view is used by the javascripts,
        fetching configuration or results"""

    def html_results(self, query):
        """html results, used for in the edit screen of a collection,
           used in the live update results"""
        options = dict(original_context=self.context)
        results = self(query, sort_on=self.request.get('sort_on', None),
                       sort_order=self.request.get('sort_order', None),
                       limit=50)
        return getMultiAdapter(
            (results, self.request),
            name='sortable_query_results'
        )(**options)

    def _makequery(self, query=None, batch=False, b_start=0, b_size=30,
                   sort_on=None, sort_order=None, limit=0, brains=False,
                   custom_query=None):
        results = super(QueryBuilder, self)._makequery(
            query, batch=False, b_start=b_start, b_size=b_size,
            sort_on=sort_on, sort_order=sort_order, limit=limit,
            brains=True, custom_query=custom_query)
        sorting = self.request.form.get('sorting', '')
        # if sorting is None make it an empty list
        sorting = isinstance(sorting, basestring) and sorting.split(',') or []
        # apply the custom sorting to the resultset according to
        # our sorting list
        positions = {j: i for i, j in enumerate(sorting)}
        results = sorted(
            results, key=lambda item: positions.get(item.UID, 999))
        if not brains:
            results = IContentListing(results)
        if batch:
            results = Batch(results, b_size, start=b_start)
        return results

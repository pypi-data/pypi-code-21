import json

from ..util import deprecation
from .contributingrecords import ContributingRecordsMixin
from .dashboards import DashboardsMixin
from .enrichments import EnrichmentsMixin
from .facets import FacetsMixin
from .globaltemp import GlobalTempMixin
from .objects import ObjectsMixin
from .projects import ProjectsMixin
from .savedsearches import SavedSearchesMixin
from .smartfilters import SmartfiltersMixin
from .subscriptions import SubscriptionsMixin
from .synonyms import SynonymsMixin
from .tasks import TasksMixin
from .themes import ThemesMixin
from .trenddetection import TrendDetectionMixin
from .widgets_assets import WidgetsAndAssetsMixin


class TopicApiBaseMixin(object):

    def get_projects(self):
        """Return all projects.
        """
        # Build URL
        url = '%(ep)s/v0/%(tenant)s/projects' % {
            'ep': self.topic_api_url,
            'tenant': self.tenant
        }
        res = self._perform_request('get', url)
        return self._process_response(res)

    def get_pipelets(self):
        """Return all available pipelets.

        These pipelets can be used for enrichments of type `pipelet`.

        :returns: A dictionary where the value for `pipelets` is a list of
            pipelets.

        Example::

            >>> client.get_pipelets()
            {u'pipelets': [{u'id': u'tenant01/textrazor',
                            u'name': u'textrazor'}]}
        """
        url = '%(ep)s/v0/%(tenant)s/pipelets' % {
            'ep': self.topic_api_url,
            'tenant': self.tenant
        }
        res = self._perform_request('get', url)
        return self._process_response(res)

    def get_version(self):
        """Get current squirro version and build number.

        :return: Dictionary contains 'version', 'build' and 'components'.
            'components' is used for numeric comparison.

        Example::

            >>> client.get_version()
            {
                "version": "2.4.5",
                "build": "2874"
                "components": [2, 4, 5]
            }
        """
        url = '%(ep)s/v0/version' % {
            'ep': self.topic_api_url,
        }
        res = self._perform_request('get', url)
        return self._process_response(res, [200])

    #
    # Items
    #
    def get_encrypted_query(self, project_id, query=None, aggregations=None,
                            fields=None, created_before=None,
                            created_after=None, options=None, **kwargs):
        """Encrypts and signs the `query` and returns it. If set the
        `aggregations`, `created_before`, `created_after`, `fields` and
        `options` are part of the encrypted query as well.

        :param project_id: Project identifier.
        :param query: query to encrypt.

        For additional parameters see `self.query()`.

        :returns: A dictionary which contains the encrypted query

        Example::

            >>> client.get_encrypted_query(
                    '2aEVClLRRA-vCCIvnuEAvQ',
                    query='test_query')
            {u'encrypted_query': 'YR4h147YAldsARmTmIrOcJqpuntiJULXPV3ZrX_'
            'blVWvbCavvESTw4Jis6sTgGC9a1LhrLd9Nq-77CNX2eeieMEDnPFPRqlPGO8V'
            'e2rlwuKuVQJGQx3-F_-eFqF-CE-uoA6yoXoPyYqh71syalWFfc-tuvp0a7c6e'
            'eKAO6hoxwNbZlb9y9pha0X084JdI-_l6hew9XKZTXLjT95Pt42vmoU_t6vh_w1'
            'hXdgUZMYe81LyudvhoVZ6zr2tzuvZuMoYtP8iMcVL_Z0XlEBAaMWAyM5hk_tAG'
            '7AbqGejZfUrDN3TJqdrmHUeeknpxpMp8nLTnbFMuHVwnj2hSmoxD-2r7BYbolJ'
            'iRFZuTqrpVi0='}
        """
        url = ('%(ep)s/%(version)s/%(tenant)s'
               '/projects/%(project_id)s/items/query_encryption')
        url = url % {
            'ep': self.topic_api_url, 'version': self.version,
            'tenant': self.tenant, 'project_id': project_id}

        headers = {'Content-Type': 'application/json'}

        args = {
            'query': query,
            'aggregations': aggregations,
            'fields': fields,
            'options': options,
            'created_before': created_before,
            'created_after': created_after,
        }
        args.update(kwargs)
        data = dict([(k, v) for k, v in args.iteritems() if v is not None])

        res = self._perform_request(
            'post', url, data=json.dumps(data), headers=headers)
        return self._process_response(res)

    def query(self, project_id, query=None, aggregations=None, start=None,
              count=None, fields=None, highlight=None, next_params=None,
              created_before=None, created_after=None, options=None,
              encrypted_query=None, **kwargs):
        """Returns items for the provided project.

        This is the successor to the `get_items` method and should be used in
        its place.

        :param project_id: Project identifier.
        :param query: Optional query to run.
        :param start: Zero based starting point.
        :param count: Maximum number of items to return.
        :param fields: Fields to return.
        :param highlight: Dictionary containing highlight information. Keys
            are: `query` (boolean) if True the response will contain highlight
            information. `smartfilters` (list): List of Smart Filter names to
            be highlighted.
        :param options: Dictionary of options that influence the
            result-set. Valid options are:

                - `fold_near_duplicates` to fold near-duplicates together and
                  filter them out of the result-stream. Defaults to False.
                - `abstract_size` to set the length of the returned abstract in
                  number of characters. Defaults to the configured
                  default_abstract_size (500).
                - `update_cache` if `False` the result won't be cached. Used
                  for non-interactive queries that iterate over a large number
                  of items. Defaults to `True`.
        :param encrypted_query: Optional Encrypted query returned by
            `get_encrypted_query` method. This parameter overrides the `query`
            parameter and `query_template_params` (as part of `options`
            parameter), if provided. Returns a 403 if the encrypted query is
            expired or has been altered with.
        :param next_params: Parameter that were sent with the previous
            response as `next_params`.
        :param created_before: Restrict result set to items created before
            `created_before`.
        :param created_after: Restrict result set to items created after
            `created_after`.
        :param kwargs: Additional query parameters. All keyword arguments are
            passed on verbatim to the API.
        """
        url = ('%(ep)s/%(version)s/%(tenant)s'
               '/projects/%(project_id)s/items/query')
        url = url % {
            'ep': self.topic_api_url, 'version': self.version,
            'tenant': self.tenant, 'project_id': project_id}

        headers = {'Content-Type': 'application/json'}

        args = {
            'query': query,
            'aggregations': aggregations,
            'start': start,
            'count': count,
            'fields': fields,
            'highlight': highlight,
            'next_params': next_params,
            'options': options,
            'created_before': created_before,
            'created_after': created_after,
            'encrypted_query': encrypted_query,
        }
        args.update(kwargs)
        data = dict([(k, v) for k, v in args.iteritems() if v is not None])

        res = self._perform_request(
            'post', url, data=json.dumps(data), headers=headers)
        return self._process_response(res)

    def scan(self, project_id, query=None, scroll='5m', count=10000,
             fields=None, highlight=None, created_before=None,
             created_after=None, options=None, encrypted_query=None):
        """
        Returns an iterator to scan through all items of a project.

        Note: For smartfilter queries this still returns at maximum 10000
        results.

        :param project_id: The id of the project you want to scan
        :param query: An optional query string to limit the items to a matching
            subset.
        :param scroll: A time to use as window to keep the search context
            active in Elastcisearch. See https://www.elastic.co/guide/en/elasticsearch/reference/2.2/search-request-scroll.html#scroll-search-context
            for more details.
        :param count: The number of results fetched per batch. You only need
            to adjust this if you e.g. have very big documents. The maximum
            value that can be set ist 10'000.
        :param fields: Fields to return
        :param highlight: Dictionary containing highlight information. Keys
            are: `query` (boolean) if True the response will contain highlight
            information. `smartfilters` (list): List of Smart Filter names to
            be highlighted.
        :param created_before: Restrict result set to items created before
            `created_before`.
        :param created_after: Restrict result set to items created after
            `created_after`.
        :param options: Dictionary of options that influence the
            result-set. Valid options are: `abstract_size` to set the length
            of the returned abstract in number of characters. Defaults to the
            configured default_abstract_size (500).

        :return: An iterator over all (matching) items.

        Open issues/current limitations:
            - ensure this works for encrypted queries too.
            - support fold_near_duplicate option
            - support smart filter queries with more than 10k results
        """
        assert scroll, '`scroll` cannot be empty for scan.'
        if options:
            assert 'fold_near_duplicate' not in options

        url = ('%(ep)s/%(version)s/%(tenant)s'
               '/projects/%(project_id)s/items/query')
        url = url % {
            'ep': self.topic_api_url, 'version': self.version,
            'tenant': self.tenant, 'project_id': project_id}

        headers = {'Content-Type': 'application/json'}

        args = {
            'query': query,
            'scroll': scroll,
            'count': min(count, 10000),
            'fields': fields,
            'highlight': highlight,
            'options': options,
            'created_before': created_before,
            'created_after': created_after,
        }
        data = dict([(k, v) for k, v in args.iteritems() if v is not None])

        items = True
        while items:
            res = self._process_response(
                self._perform_request(
                    'post', url, data=json.dumps(data), headers=headers
                )
            )
            items = res.get('items', [])
            for item in items:
                yield item
            if not res.get('eof'):
                data['next_params'] = res.get('next_params')
            else:
                break

    def get_items(self, project_id, **kwargs):
        """Returns items for the provided project.

        DEPRECATED. The `query` method is more powerful.

        :param project_id: Project identifier.
        :param kwargs: Query parameters. All keyword arguments are passed on
            verbatim to the API. See the [[Items#List Items|List Items]]
            resource for all possible parameters.
        :returns: A dictionary which contains the items for the project.

        Example::

            >>> client.get_items('2aEVClLRRA-vCCIvnuEAvQ', count=1)
            {u'count': 1,
             u'eof': False,
             u'items': [{u'created_at': u'2012-10-06T08:27:58',
                         u'id': u'haG6fhr9RLCm7ZKz1Meouw',
                         u'link': u'https://www.youtube.com/...',
                         u'read': True,
                         u'item_score': 0.5,
                         u'score': 0.56,
                         u'sources': [{u'id': u'oMNOQ-3rQo21q3UmaiaLHw',
                                       u'link': u'https://gdata.youtube...',
                                       u'provider': u'feed',
                                       u'title': u'Uploads by mymemonic'},
                                      {u'id': u'H4nd0CasQQe_PMNDM0DnNA',
                                       u'link': None,
                                       u'provider': u'savedsearch',
                                       u'title': u'Squirro Alerts for "mmonic"'
                                      }],
                         u'starred': False,
                         u'thumbler_url': u'[long url]...jpg',
                         u'title': u'Web Clipping - made easy with Memonic',
                         u'objects': [],
                         u'webshot_height': 360,
                         u'webshot_url': u'http://webshot.trunk....jpg',
                         u'webshot_width': 480}],
             u'now': u'2012-10-11T14:39:54'}

        """
        deprecation("Please use the query method instead.")

        url = ('%(ep)s/%(version)s/%(tenant)s'
               '/projects/%(project_id)s/items')
        url = url % {
            'ep': self.topic_api_url, 'version': self.version,
            'tenant': self.tenant, 'project_id': project_id}
        print url

        res = self._perform_request('get', url, params=kwargs)
        return self._process_response(res)

    def get_item(self, project_id, item_id, **kwargs):
        """Returns the requested item for the provided project.

        :param project_id: Project identifier.
        :param item_id: Item identifier.
        :param kwargs: Query parameters. All keyword arguments are passed on
            verbatim to the API. See the [[Items#Get Item|Get Item]] resource
            for all possible parameters.
        :returns: A dictionary which contains the individual item.

        Example::

            >>> client.get_item(
            ...     '2aEVClLRRA-vCCIvnuEAvQ', 'haG6fhr9RLCm7ZKz1Meouw')
            {u'item': {u'created_at': u'2012-10-06T08:27:58',
                       u'id': u'haG6fhr9RLCm7ZKz1Meouw',
                       u'link': u'https://www.youtube.com/watch?v=Zzvhu42dWAc',
                       u'read': True,
                       u'item_score': 0.5,
                       u'score': 0.56,
                       u'sources': [{u'id': u'oMNOQ-3rQo21q3UmaiaLHw',
                                     u'link': u'https://gdata.youtube.com/...',
                                     u'provider': u'feed',
                                     u'title': u'Uploads by mymemonic'},
                                    {u'id': u'H4nd0CasQQe_PMNDM0DnNA',
                                     u'link': None,
                                     u'provider': u'savedsearch',
                                     u'title': u'Squirro Alerts for "memonic"'}
                                   ],
                       u'starred': False,
                       u'thumbler_url': u'[long url]...jpg',
                       u'title': u'Web Clipping - made easy with Memonic',
                       u'objects': [],
                       u'webshot_height': 360,
                       u'webshot_url': u'http://webshot.trunk....jpg',
                       u'webshot_width': 480}}

        """

        url = ('%(ep)s/%(version)s/%(tenant)s'
               '/projects/%(project_id)s/items/%(item_id)s')
        url = url % {
            'ep': self.topic_api_url, 'version': self.version,
            'tenant': self.tenant, 'project_id': project_id,
            'item_id': item_id}

        res = self._perform_request('get', url, params=kwargs)
        return self._process_response(res)

    def modify_item(self, project_id, item_id, star=None, read=None,
                    keywords=None):
        """Updates the flags and keywords of an item.

        :param project_id: Project identifier.
        :param item_id: Item identifier.
        :param star: Starred flag for the item, either `True` or `False`.
        :param read: Read flag for the item, either `True` or `False`.
        :param keywords: Overwrites all `keywords` of the item.

        Example::

            >>> client.modify_item(
            ...     '2aEVClLRRA-vCCIvnuEAvQ', 'haG6fhr9RLCm7ZKz1Meouw',
            ...     star=True, read=False, keywords={'Canton': ['Berne'],
            ...                                      'Topic': None})

        """

        url = ('%(ep)s/%(version)s/%(tenant)s'
               '/projects/%(project_id)s/items/%(item_id)s')
        url = url % {
            'ep': self.topic_api_url, 'version': self.version,
            'tenant': self.tenant, 'project_id': project_id,
            'item_id': item_id}

        # build item state
        state = {}
        if star is not None:
            state['starred'] = star
        if read is not None:
            state['read'] = read

        data = {'state': state}

        if keywords is not None:
            data['keywords'] = keywords

        headers = {'Content-Type': 'application/json'}

        res = self._perform_request(
            'put', url, data=json.dumps(data), headers=headers)
        self._process_response(res, [204])

    def delete_item(self, project_id, item_id, object_ids=None):
        """Deletes an item. If `object_ids` is provided the item gets not
        deleted but is de-associated from these objects.

        :param project_id: Project identifier.
        :param item_id: Item identifier.
        :param object_ids: Object identifiers from which the item is
            de-associated.

        Example::

            >>> client.delete_item(
            ...     '2aEVClLRRA-vCCIvnuEAvQ', 'haG6fhr9RLCm7ZKz1Meouw',
            ...     object_ids=['object01'])
        """

        url = ('%(ep)s/%(version)s/%(tenant)s'
               '/projects/%(project_id)s/items/%(item_id)s')
        url = url % {
            'ep': self.topic_api_url, 'version': self.version,
            'tenant': self.tenant, 'project_id': project_id,
            'item_id': item_id}

        # build params
        params = {}
        if object_ids:
            params['object_ids'] = ','.join(object_ids)

        res = self._perform_request('delete', url, params=params)
        self._process_response(res, [204])

    #
    #
    # Typeahead
    #

    def get_typeahead_suggestions(self, project_id, searchbar_query,
                                  cursor_pos, max_suggestions=None,
                                  options=None, filter_query=None):
        """Get the typeahead suggestions for a query `searchbar_query` in the
        project identified by the id `project_id`.

        :param project_id: Project identifier from which the typeahead
            suggestions should be returned.
        :param searchbar_query: The full query that goes into a searchbar. The
            `searchbar_query` will automatically be parsed and the suggestion
            on the field defined by the `cursor_pos` and filtered by the rest
            of the query will be returned. `searchbar_query` can not be None.
        :param cursor_pos: The position in the searchbar_query on which the
            typeahead is needed. `cursor_pos` parameter follow a 0-index
            convention, i.e. the first position in the searchbar-query is 0.
            `cursor_pos` should be a positive integer.
        :param max_suggestions: Maximum number of typeahead suggestions to be
            returned. `max_suggestions` should be a non-negative integer.
        :param options: Dictionary of options that influence the result-set.
            Valid options are: `template_params` dict containing the query
            template parameters
        :param filter_query: Squirro query to limit the typeahead suggestions.
            Must be of type `string`. Defaults to `None` if not specified. As
            an example, this parameter can be used to filter the typeahead
            suggestions by a dashboard query on a Squirro dashboard.

        :returns: A dict of suggestions

        Example::

            >>> client.get_typeahead_suggestions(
                    project_id='Sz7LLLbyTzy_SddblwIxaA',
                    'searchbar_query='Country:India c',
                    'cursor_pos'=15)

                {u'suggestions': [{
                    u'type': u'facetvalue', u'key': u'Country:India
                    City:Calcutta', u'value': u'city:Calcutta', 'score': 12,
                    'cursor_pos': 26, 'group': 'country'},

                    {u'type': u'facetvalue', u'key': u'Country:India
                    Name:Caesar', u'value': u'name:Caesar', 'score': 8,
                    'cursor_pos': 24, 'group': 'country'},

                    {u'type': u'facetname', u'key': u'Country:India city:',
                    u'value': u'City', 'score': 6, 'cursor_pos': 19, 'group':
                    'Fields'}]}
        """

        # construct the url
        url = ('%(ep)s/%(version)s/%(tenant)s'
               '/projects/%(project_id)s/typeahead')
        url = url % {
            'ep': self.topic_api_url, 'version': self.version,
            'tenant': self.tenant, 'project_id': project_id}

        # prepare the parameters dict
        params = {}
        params['searchbar_query'] = searchbar_query
        params['cursor_pos'] = cursor_pos
        params['max_suggestions'] = max_suggestions
        params['filter_query'] = filter_query

        if options:
            params['options'] = json.dumps(options)

        # issue request
        res = self._perform_request('get', url, params=params)

        return self._process_response(res)

    #
    # Preview
    #

    def get_preview(self, project_id, provider, config):
        """Preview the provider configuration.

        :param project_id: Project identifier.
        :param provider: Provider name.
        :param config: Provider configuration.
        :returns: A dictionary which contains the provider preview items.

        Example::

            >>> client.get_preview('feed', {'url': ''})
            {u'count': 2,
             u'items': [{u'created_at': u'2012-10-01T20:12:07',
                         u'id': u'F7EENNQeTz2z7O7htPACgw',
                         u'link': u'http://blog.squirro.com/post/32680369129/',
                         u'read': False,
                         u'item_score': 0,
                         u'score': 0,
                         u'starred': False,
                         u'thumbler_url': u'[long url ...]/...jpg',
                         u'title': u'Swisscom features our sister product',
                         u'webshot_height': 237,
                         u'webshot_url': u'http://webshot.trunk...',
                         u'webshot_width': 600},
                        {u'created_at': u'2012-09-25T08:09:24',
                         u'id': u'Nrj308UNTEixra3qTYLn7w',
                         u'link': u'http://blog.squirro.com/post/32253089480/',
                         u'read': False,
                         u'item_score': 0,
                         u'score': 0,
                         u'starred': False,
                         u'thumbler_url': u'[long url ...]/...jpg',
                         u'title': u'247 million emails are sent every day...',
                         u'webshot_height': 360,
                         u'webshot_url': u'http://webshot.trunk...',
                         u'webshot_width': 480}]}

        """

        url = ('%(ep)s/%(version)s/%(tenant)s/projects/%(project_id)s/'
               'preview') % {
                   'ep': self.topic_api_url, 'project_id': project_id,
                   'version': self.version, 'tenant': self.tenant}

        # build params
        params = {'provider': provider, 'config': json.dumps(config)}

        res = self._perform_request('get', url, params=params)
        return self._process_response(res)


class TopicApiMixin(
    TopicApiBaseMixin, ContributingRecordsMixin, DashboardsMixin,
    EnrichmentsMixin, FacetsMixin, GlobalTempMixin, ObjectsMixin, ProjectsMixin,
    SavedSearchesMixin, SmartfiltersMixin, SubscriptionsMixin, SynonymsMixin,
    TasksMixin, ThemesMixin, TrendDetectionMixin, WidgetsAndAssetsMixin):
    pass

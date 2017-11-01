"""
Relevance Elastic engine.

This module provides the storage and search engine connector for ElasticSearch instances.
"""

import copy
import typing
import requests
import datetime
import warnings
import logging
from collections import OrderedDict

from relevance.query import Search
from relevance.query import LogicalOperator
from relevance.query import ComparisonOperator
from relevance.facet import TermFacet
from relevance.facet import HistogramFacet
from relevance.facet import DateFacet
from relevance.facet import IntervalFacet
from relevance.facet import RangeFacet
from relevance.facet import FacetNotDefinedError
from relevance.facet import FacetNotSupportedWarning
from relevance.engine import SearchEngine
from relevance.engine import MappingEngine
from relevance.engine import IngestionEngine
from relevance.engine import EngineError
from relevance.engine import MappingError
from relevance.engine import SearchError
from relevance.engine import IngestionError
from relevance.mapping import Mapping
from relevance.mapping import Field
from relevance.mapping import ObjectField
from relevance.document import Document
from relevance.document import Result
from relevance.document import ResultSet


# Logging
logger = logging.getLogger('relevance.engine.elastic')


class ElasticEngine(SearchEngine, MappingEngine, IngestionEngine):
    """
    ElasticSearch storage engine.

    This class provides the storage and search engine for ElasticSearch.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the engine.
        """
        SearchEngine.__init__(self, *args, **kwargs)
        MappingEngine.__init__(self, *args, **kwargs)
        IngestionEngine.__init__(self, *args, **kwargs)
        self.session = None

    def to_dsl(self, search: Search) -> dict:
        """
        Transform a search object into a query DSL.

        :param search: the input search object.
        :returns: the resulting ElasticSearch query DSL.
        """
        def build_query(query):
            """
            Build a query into a DSL.
            """
            result = []

            # Logical operator
            if query.logic == LogicalOperator.AND:
                operator = 'must'
            elif query.logic == LogicalOperator.OR:
                operator = 'should'
            elif query.logic == LogicalOperator.NOT:
                operator = 'must_not'
            else:
                raise TypeError('unknown operator {0}'.format(query.logic))

            # Query terms
            for x in query.terms:
                result.append({'match': {'_all': x}})

            # Query filters
            for field, op, value in query.facets:
                start, end = value, value
                part = ref = {}

                # Manual facet definition
                try:
                    facet_def = self.facets[field]

                    if facet_def.path is not None:
                        field = facet_def.path

                        path = []
                        for x in facet_def.path.split('.')[:-1]:
                            path.append(x)
                            ref.update({
                                'nested': {
                                    'path': '.'.join(path),
                                    'query': {},
                                },
                            })
                            ref = ref['nested']['query']
                    elif facet_def.field is not None:
                        field = facet_def.field

                    if isinstance(facet_def, HistogramFacet):
                        start, end = facet_def.get_range_for(value)

                # Auto facet definition
                except (KeyError, TypeError):
                    if not self.auto_filters:
                        raise FacetNotDefinedError(field)

                # Filter operator
                if value is None:
                    if op == ComparisonOperator.EQ:
                        ref.update({'missing': {'field': field}})
                    else:
                        ref.update({'exists': {'field': field}})
                elif op == ComparisonOperator.EQ and start == end:
                    ref.update({'term': {field: value}})
                elif op == ComparisonOperator.NEQ and start == end:
                    ref.update({'bool': {'must_not': {'term': {field: value}}}})
                elif op == ComparisonOperator.EQ and start != end:
                    ref.update({'range': {field: {'gte': start, 'lt': end}}})
                elif op == ComparisonOperator.NEQ and start != end:
                    ref.update({'range': {field: {'lt': start, 'gte': end}}})
                elif op == ComparisonOperator.GT:
                    ref.update({'range': {field: {'gt': start}}})
                elif op == ComparisonOperator.LT:
                    ref.update({'range': {field: {'lt': end}}})
                elif op == ComparisonOperator.GTE:
                    ref.update({'range': {field: {'gte': start}}})
                elif op == ComparisonOperator.LTE:
                    ref.update({'range': {field: {'lte': end}}})
                else:
                    raise TypeError('unknown operator {0}'.format(op))

                result.append(part)

            # Sub queries
            for x in query.queries:
                result.append(build_query(x))

            dsl = {'bool': {operator: result}}
            if operator == 'should':
                dsl['bool']['minimum_should_match'] = 1

            logger.debug('parsed {0} into query dsl: {1}'.format(
                query, dsl,
            ))
            return dsl

        def build_facets(search):
            """
            Build a search object into a aggregations DSL.
            """
            lst = list(self.facets) if search.facets is None else search.facets
            aggs = {}

            for field in lst:
                part = {field: {}}
                ref = part[field]

                # Manual facet definition
                try:
                    facet_def = self.facets[field]

                    if facet_def.path is not None:
                        field = facet_def.path

                        path = []
                        for x in facet_def.path.split('.')[:-1]:
                            path.append(x)
                            ref.update({
                                'nested': {
                                    'path': '.'.join(path),
                                },
                                'aggs': {'_nested': {}},
                            })
                            ref = ref['aggs']['_nested']
                    elif facet_def.field is not None:
                        field = facet_def.field

                # Auto facet definition
                except (KeyError, TypeError):
                    if not self.auto_filters:
                        raise FacetNotDefinedError(field)

                    facet_def = TermFacet(field)

                if isinstance(facet_def, TermFacet):
                    ref.update({
                        'terms': {'field': field}
                    })

                elif isinstance(facet_def, DateFacet):
                    ref.update({
                        'date_histogram': {
                            'field': field,
                            'interval': facet_def.interval,
                        }
                    })

                elif isinstance(facet_def, IntervalFacet):
                    ref.update({
                        'histogram': {
                            'field': field,
                            'interval': facet_def.interval,
                        }
                    })

                elif isinstance(facet_def, RangeFacet):
                    ref.update({
                        'range': {
                            'field': field,
                            'keyed': True,
                            'ranges': [{'key': k, 'from': v[0], 'to': v[1]}
                                       for k, v in facet_def.ranges.items()],
                        },
                    })

                else:
                    logger.warn('facet type not supported by engine: {0}'.format(
                        facet_def,
                    ))
                    warnings.warn(FacetNotSupportedWarning(facet_def))

                aggs.update(part)

            if len(aggs) > 0:
                logger.debug('parsed {0} into facets dsl: {1}'.format(
                    search, aggs,
                ))
                return aggs

        dsl = {}

        if search.queries is not None:
            dsl.update({
                'query': build_query(search.queries),
            })

        if search.slices:
            dsl.update({
                'from': search.slices[0],
                'size': search.slices[1],
            })

        if search.sorts:
            dsl.update({
                'sort': dict([(k, v.value) for k, v in search.sorts]),
            })

        if search.facets is None or len(search.facets) > 0:
            aggs = build_facets(search)
            if aggs is not None:
                dsl.update({
                    'aggs': aggs,
                })

        logger.debug('parsed {0} into search dsl: {1}'.format(
            search, dsl,
        ))
        return dsl

    def search(self, search: Search) -> ResultSet:
        """
        Perform a search request on the engine.

        This method automatically transforms the search object into a query DSL, sends it
        and parses the result as a resultset object.
        """
        if self.session is None:
            raise IOError('engine not started')

        super().search(search)

        url = '{0}/{1}_search'.format(
            self.target,
            ','.join(search.doc_types) + '/' if search.doc_types is not None else '',
        )
        payload = self.to_dsl(search)

        logger.debug('sending POST to {0} with {1} bytes payload'.format(
            url, len(payload),
        ))

        try:
            results = ResultSet()
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            response = response.json()
            results.time_end = datetime.datetime.now()
            results.count = response['hits']['total']
        except self.session.exceptions.HTTPError as e:
            raise SearchError(str(e))
        except Exception as e:
            raise EngineError(str(e))

        logger.debug('received response: {0}'.format(
            response,
        ))

        for x in response['hits']['hits']:
            result = Result(x['_index'], x['_type'], x['_id'], score=x['_score'])
            result.update(x['_source'])
            results.append(result)

        if 'aggregations' in response:
            results.facets = {}
            for name, data in response['aggregations'].items():
                results.facets[name] = OrderedDict()

                ref = data
                while '_nested' in ref:
                    ref = ref['_nested']

                if 'buckets' not in ref:
                    continue

                if isinstance(ref['buckets'], dict):
                    for x, y in ref['buckets'].items():
                        results.facets[name][x] = y['doc_count']
                elif isinstance(ref['buckets'], list):
                    for x in ref['buckets']:
                        key = x.get('key_as_string', x.get('key'))
                        results.facets[name][key] = x['doc_count']

        return results

    def get_doc_types(self) -> typing.List[str]:
        """
        Get a list of available document types.
        """
        if self.session is None:
            raise IOError('engine not started')

        url = '{0}/_mapping'.format(self.target)

        logger.debug('sending GET to {0}'.format(
            url,
        ))

        try:
            response = self.session.get(url)
            response.raise_for_status()
            response = response.json()
        except self.session.exceptions.HTTPError as e:
            raise MappingError(str(e))
        except Exception as e:
            raise EngineError(str(e))

        logger.debug('received response: {0}'.format(
            response,
        ))

        result = set()
        for index in response:
            try:
                for doc_type in response[index]['mappings']:
                    result.add(doc_type)
            except KeyError:
                pass

        return list(result)

    def get_mapping(self, doc_type: str) -> Mapping:
        """
        Get the mapping object for a specific document type.
        """
        if self.session is None:
            raise IOError('engine not started')

        url = '{0}/_mapping'.format(self.target)

        logger.debug('sending GET to {0}'.format(
            url,
        ))

        try:
            response = self.session.get(url)
            response.raise_for_status()
            response = response.json()
        except self.session.exceptions.HTTPError as e:
            raise MappingError(str(e))
        except Exception as e:
            raise EngineError(str(e))

        logger.debug('received response: {0}'.format(
            response,
        ))

        for index in response:
            def build_mapping(properties):
                """
                Build a mapping object from a properties dict.
                """
                mapping = Mapping()

                for key, conf in properties.items():
                    options = dict(
                        stored=conf.get('store', False),
                        indexed=conf.get('index', False),
                    )

                    if conf['type'] == 'string':
                        field = Field(key, str, **options)
                    if conf['type'] in ('long', 'integer'):
                        field = Field(key, int, **options)
                    if conf['type'] == 'double':
                        field = Field(key, float, **options)
                    if conf['type'] == 'boolean':
                        field = Field(key, bool, **options)
                    if conf['type'] == 'object':
                        field = Field(key, dict, **options)
                    if conf['type'] == 'binary':
                        field = Field(key, bytes, **options)
                    if conf['type'] == 'date':
                        field = Field(key, datetime.datetime, **options)
                    if conf['type'] == 'nested':
                        field = ObjectField(key, build_mapping(conf['properties']))

                    mapping = mapping.add(field)

                return mapping

            try:
                properties = response[index]['mappings'][doc_type]['properties']
            except KeyError:
                continue

            return build_mapping(properties)

        raise MappingError('no mapping for {0}'.format(doc_type))

    def put_mapping(self, doc_type: str, mapping: Mapping):
        """
        Update the mapping for a specific document type.
        """
        if self.session is None:
            raise IOError('engine not started')

        raise NotImplementedError()

    def publish(self, doc: Document) -> Document:
        """
        Index a document.
        """
        if self.session is None:
            raise IOError('engine not started')

        url = '{0}/{1}/{2}'.format(self.target, doc.schema, doc.doc_type)

        payload = dict(doc)
        if doc.uid is not None:
            payload['_id'] = doc.uid

        logger.debug('sending POST to {0} with {1} bytes payload'.format(
            url, len(payload),
        ))

        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            response = response.json()
        except self.session.exceptions.HTTPError as e:
            raise IngestionError(str(e))
        except Exception as e:
            raise EngineError(str(e))

        logger.debug('received response: {0}'.format(
            response,
        ))

        doc = copy.deepcopy(doc)
        doc.uid = response.get('_id', doc.uid)
        return doc

    def unpublish(self, schema: str, doc_type: str, uid: object):
        """
        Delete a document.
        """
        if self.session is None:
            raise IOError('engine not started')

        url = '{0}/{1}/{2}/{3}'.format(self.target, schema, doc_type, uid)

        logger.debug('sending DELETE to {0}'.format(
            url,
        ))

        try:
            response = self.session.delete(url)
            response.raise_for_status()
        except self.session.exceptions.HTTPError as e:
            raise IngestionError(str(e))
        except Exception as e:
            raise EngineError(str(e))

        logger.debug('received response: {0}'.format(
            response,
        ))

    def get_status(self) -> typing.Dict[str, object]:
        """
        Get the indexer state.
        """
        if self.session is None:
            raise IOError('engine not started')

        url = '{0}/_stats'.format(self.target)

        logger.debug('sending GET to {0}'.format(
            url,
        ))

        try:
            response = self.session.get(url)
            response.raise_for_status()
            response = response.json()['_all']['total']
        except Exception as e:
            raise EngineError(str(e))

        logger.debug('received response: {0}'.format(
            response,
        ))

        return {
            'indexed': response['indexing']['index_total'],
            'deleted': response['indexing']['delete_total'],
            'commits': response['refresh']['total'],
            'size': response['store']['size_in_bytes'],
        }

    def start(self):
        """
        Start the engine.
        """
        if self.session is not None:
            return

        self.session = requests.Session()
        self.session.get(self.target)

    def stop(self):
        """
        Stop the engine.
        """
        if self.session is None:
            return

        self.session.close()
        self.session = None

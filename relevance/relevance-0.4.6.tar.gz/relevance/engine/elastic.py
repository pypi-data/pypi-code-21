"""
This module implements the search backend for ElasticSearch instances.
"""

import copy
import typing
import datetime
import warnings
from collections import OrderedDict
import requests

from relevance import loggers
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
from relevance.engine import Engine
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
logger = loggers.getLogger('relevance.engine.elastic')  # pylint: disable=invalid-name


class ElasticEngine(Engine):
    """
    This is the engine implementation for ElasticSearch backends.
    """
    def __init__(self, *args, **kwargs):
        """
        .. init
        """
        super().__init__(*args, **kwargs)
        self.session = None

    def to_dsl(self, search: Search) -> dict:
        """
        Transform a search object into a query DSL.

        :param search: the input search object.
        :return: the resulting ElasticSearch query DSL.
        """
        def build_query(query):  # pylint: disable=too-many-branches,too-many-statements
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
            for term in query.terms:
                result.append({'match': {'_all': term}})

            # Query filters
            for field, comp, value in query.facets:
                start, end = value, value
                part = ref = {}

                # Manual facet definition
                try:
                    facet_def = self.facets[field]

                    if facet_def.path is not None:
                        field = facet_def.path

                        path = []
                        for part in facet_def.path.split('.')[:-1]:
                            path.append(part)
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
                    if comp == ComparisonOperator.EQ:
                        ref.update({'missing': {'field': field}})
                    else:
                        ref.update({'exists': {'field': field}})
                elif comp == ComparisonOperator.EQ and start == end:
                    ref.update({'term': {field: value}})
                elif comp == ComparisonOperator.NEQ and start == end:
                    ref.update({'bool': {'must_not': {'term': {field: value}}}})
                elif comp == ComparisonOperator.EQ and start != end:
                    ref.update({'range': {field: {'gte': start, 'lt': end}}})
                elif comp == ComparisonOperator.NEQ and start != end:
                    ref.update({'range': {field: {'lt': start, 'gte': end}}})
                elif comp == ComparisonOperator.GT:
                    ref.update({'range': {field: {'gt': start}}})
                elif comp == ComparisonOperator.LT:
                    ref.update({'range': {field: {'lt': end}}})
                elif comp == ComparisonOperator.GTE:
                    ref.update({'range': {field: {'gte': start}}})
                elif comp == ComparisonOperator.LTE:
                    ref.update({'range': {field: {'lte': end}}})
                else:
                    raise TypeError('unknown operator {0}'.format(comp))

                result.append(part)

            # Sub queries
            for subquery in query.queries:
                result.append(build_query(subquery))

            dsl = {'bool': {operator: result}}
            if operator == 'should':
                dsl['bool']['minimum_should_match'] = 1

            logger.debug('query to dsl', query=query, dsl=dsl)
            return dsl

        def build_facets(search):
            """
            Build a search object into a aggregations DSL.
            """
            lst = list(self.facets) if search.facets is None else search.facets
            aggs = {}

            for field in lst:
                agg = {field: {}}
                ref = agg[field]

                # Manual facet definition
                try:
                    facet_def = self.facets[field]

                    if facet_def.path is not None:
                        field = facet_def.path

                        path = []
                        for part in facet_def.path.split('.')[:-1]:
                            path.append(part)
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

                    facet_def = TermFacet(field=field)

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
                    logger.warning('facet type not supported', type=facet_def.__class__)
                    warnings.warn(FacetNotSupportedWarning(facet_def))

                aggs.update(agg)

            if aggs:
                logger.debug('facets to dsl', facets=lst, dsl=aggs)
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

        if search.facets is None or search.facets:
            aggs = build_facets(search)
            if aggs is not None:
                dsl.update({
                    'aggs': aggs,
                })

        logger.debug('search to dsl', search=search, dsl=dsl)
        return dsl

    def search(self, search: Search) -> ResultSet:
        """
        Implementation of :meth:`.engine.Engine.search`.
        """
        if self.session is None:
            raise IOError('engine not started')

        super().search(search)

        url = '{0}/{1}_search'.format(
            self.target,
            ','.join(search.doc_types) + '/' if search.doc_types is not None else '',
        )
        payload = self.to_dsl(search)

        logger.debug('http POST', url=url, length=len(payload))

        try:
            results = ResultSet()
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            response = response.json()
            results.time_end = datetime.datetime.now()  # type: ignore
            results.total_count = response['hits']['total']
        except requests.exceptions.HTTPError as ex:
            raise SearchError(str(ex))
        except Exception as ex:
            raise EngineError(str(ex))

        logger.debug('http response', response=response)

        for item in response['hits']['hits']:
            result = Result(item['_index'], item['_type'], item['_id'], score=item['_score'])
            result.update(item['_source'])
            results.append(result)

        if 'aggregations' in response:
            results.facets = {}  # type: ignore
            for name, data in response['aggregations'].items():
                results.facets[name] = OrderedDict()

                ref = data
                while '_nested' in ref:
                    ref = ref['_nested']

                if 'buckets' not in ref:
                    continue

                if isinstance(ref['buckets'], dict):
                    for key, value in ref['buckets'].items():
                        results.facets[name][key] = value['doc_count']
                elif isinstance(ref['buckets'], list):
                    for value in ref['buckets']:
                        key = value.get('key_as_string', value.get('key'))
                        results.facets[name][key] = value['doc_count']

        return results

    def get_doc_types(self) -> typing.List[str]:
        """
        Implementation of :meth:`.engine.Engine.get_doc_types`.
        """
        if self.session is None:
            raise IOError('engine not started')

        url = '{0}/_mapping'.format(self.target)

        logger.debug('http GET', url=url)

        try:
            response = self.session.get(url)
            response.raise_for_status()
            response = response.json()
        except requests.exceptions.HTTPError as ex:
            raise MappingError(str(ex))
        except Exception as ex:
            raise EngineError(str(ex))

        logger.debug('http response', response=response)

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
        Implementation of :meth:`.engine.Engine.get_mapping`.
        """
        if self.session is None:
            raise IOError('engine not started')

        url = '{0}/_mapping'.format(self.target)

        logger.debug('http GET', url=url)

        try:
            response = self.session.get(url)
            response.raise_for_status()
            response = response.json()
        except requests.exceptions.HTTPError as ex:
            raise MappingError(str(ex))
        except Exception as ex:
            raise EngineError(str(ex))

        logger.debug('http response', response=response)

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

                    mapping.add(field)

                return mapping

            try:
                properties = response[index]['mappings'][doc_type]['properties']
            except KeyError:
                continue

            return build_mapping(properties)

        raise MappingError('no mapping for {0}'.format(doc_type))

    def put_mapping(self, doc_type: str, mapping: Mapping):
        """
        Implementation of :meth:`.engine.Engine.put_mapping`.
        """
        if self.session is None:
            raise IOError('engine not started')

        raise NotImplementedError()

    def publish(self, doc: Document) -> Document:
        """
        Implementation of :meth:`.engine.Engine.publish`.
        """
        if self.session is None:
            raise IOError('engine not started')

        url = '{0}/{1}/{2}'.format(self.target, doc.schema, doc.doc_type)

        payload = dict(doc)
        if doc.uid is not None:
            payload['_id'] = doc.uid

        logger.debug('http POST', url=url, length=len(payload))

        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            response = response.json()
        except requests.exceptions.HTTPError as ex:
            raise IngestionError(str(ex))
        except Exception as ex:
            raise EngineError(str(ex))

        logger.debug('http response', response=response)

        doc = copy.deepcopy(doc)
        doc.uid = response.get('_id', doc.uid)
        return doc

    def unpublish(self, schema: str, doc_type: str, uid: object):
        """
        Implementation of :meth:`.engine.Engine.unpublish`.
        """
        if self.session is None:
            raise IOError('engine not started')

        url = '{0}/{1}/{2}/{3}'.format(self.target, schema, doc_type, uid)

        logger.debug('http DELETE', url=url)

        try:
            response = self.session.delete(url)
            response.raise_for_status()
        except requests.HTTPError as ex:
            raise IngestionError(str(ex))
        except Exception as ex:
            raise EngineError(str(ex))

        logger.debug('http response', response=response)

    def start(self):
        """
        Implementation of :meth:`.engine.Engine.start`.
        """
        if self.session is not None:
            return

        logger.info('start', id=id(self.session))

        self.session = requests.Session()
        self.session.get(self.target)

    def stop(self):
        """
        Implementation of :meth:`.engine.Engine.stop`.
        """
        if self.session is None:
            return

        logger.info('stop', id=id(self.session))

        self.session.close()
        self.session = None

    def get_status(self) -> typing.Dict[str, object]:
        """
        Get the indexer state.

        :return: a dictionary containing various information about the status.
        """
        if self.session is None:
            raise IOError('engine not started')

        url = '{0}/_stats'.format(self.target)

        logger.debug('http GET', url=url)

        try:
            response = self.session.get(url)
            response.raise_for_status()
            response = response.json()['_all']['total']
        except Exception as ex:
            raise EngineError(str(ex))

        logger.debug('http response', response=response)

        return {
            'indexed': response['indexing']['index_total'],
            'deleted': response['indexing']['delete_total'],
            'commits': response['refresh']['total'],
            'size': response['store']['size_in_bytes'],
        }

from aws_requests_auth.boto_utils import BotoAWSRequestsAuth
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch.helpers import bulk
from elasticsearch_dsl import Search, Index, MultiSearch

class ElasticsearchProxy(object):


    def __init__(self, endpoint, region, index):
        self.auth = BotoAWSRequestsAuth(aws_host=endpoint,
                                        aws_region=region,
                                        aws_service='es')
        self.client = Elasticsearch(host=endpoint,
                                    http_auth=self.auth,
                                    port=80,
                                    connection_class=RequestsHttpConnection)
        self.index = Index(index, using=self.client)
        self.index_name = index
        self.indexed_fields, self.text_fields = self.get_indexed_fields()


    def get_indexed_fields(self):
        indexed_fields = set()
        text_fields = set()
        mappings = self.index.get_mapping().get(self.index_name, {}).get('mappings', {}).values()
        for mapping in mappings:
            for prop, prop_value in mapping.get('properties', {}).items():
                child_properties = prop_value.get('properties')
                # flatten the nested field names
                if child_properties:
                    for child_prop, child_value in child_properties.items():
                        child_prop_name = '.'.join([prop, child_prop])
                        text_fields = text_fields if child_value.get('type') != 'text' \
                                      else text_fields | {child_prop_name}
                        indexed_fields.add(child_prop_name)
                else:
                    text_fields = text_fields if prop_value.get('type') != 'text'\
                                  else text_fields | {prop}
                    indexed_fields.add(prop)
        return indexed_fields, text_fields


    def search(self, asset_manager_ids, queries=[], filters={}, sort_fields=None,
               page_no=1, page_size=100, threshold=None):
        # force to have asset_manager_ids filter
        if not asset_manager_ids:
            raise ValueError('An asset manager id is required.')
        filters.pop('asset_manager_id', [])
        field_filters = [{field if field not in self.text_fields
                          else '{}.keyword'.format(field): filter_value}
                         for field, filter_value in filters.items()]

        multi_search = MultiSearch(using=self.client, index=self.index_name)
        for search_settings in [{'type': 'phrase', 'boost': 27},
                                {'type': 'phrase_prefix', 'boost': 9},
                                {'type': 'best_fields', 'boost': 3},
                                {'type': 'best_fields', 'fuzziness': 'AUTO', 'boost': 1}]:
            search = Search(index=self.index_name).filter('terms', asset_manager_id=asset_manager_ids)
            for field_filter in field_filters:
                search = search.filter('terms', **field_filter)
            for query_arg, fields in queries:
                if query_arg:
                    search_settings['query'] = query_arg
                    search_settings['fields'] = fields
                    search = search.query('multi_match', **search_settings)
            if sort_fields:
                sort_fields = ['{}.keyword'.format(field)
                               if field.replace('-', '') in self.text_fields else field
                               for field in sort_fields]
                search = search.sort(*sort_fields)
            # paging might not be reliable for multisearch
            multi_search = multi_search.add(search[page_no-1:page_size])
        results = multi_search.execute()
        response = {}
        hits = []
        unique_hits = set()
        for result in results:
            for hit in result.hits:
                if hit.meta.id in unique_hits:
                    continue
                item = hit.to_dict()
                item.update({'_score': hit.meta.score})
                hits.append(item)
                unique_hits.add(hit.meta.id)

        max_score = max((hit['_score'] for hit in hits)) if hits else 0
        hits = hits if not threshold else [hit for hit in hits
                                           if ((hit['_score'] / max_score) * 100) >= threshold]
        response = {'total': len(hits),
                    'max_score': max_score,
                    'hits': hits}
        return response


    def bulk_update(self, documents):
        bulk(self.client, documents)
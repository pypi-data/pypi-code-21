from aws_requests_auth.boto_utils import BotoAWSRequestsAuth
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch.helpers import bulk
from elasticsearch_dsl import Search, Index

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

        for query_type in ['multi_match', 'query_string']:
            hits = []
            # give exact matches 3x more weight than fuzzy matches
            for fuzziness, boost in [(0, 3), ('Auto', 1)]:
                search = Search(using=self.client, index=self.index_name) \
                            .filter('terms', asset_manager_id=asset_manager_ids)
                for field_filter in field_filters:
                    search = search.filter('terms', **field_filter)
                for query_arg, fields in queries:
                    if query_arg:
                        search = search.query(query_type,
                                            query=query_arg if query_type != 'query_string' else '*{}*'.format(query_arg),
                                            fields=fields,
                                            boost=boost,
                                            fuzziness=fuzziness)
                if sort_fields:
                    sort_fields = ['{}.keyword'.format(field)
                                if field.replace('-', '') in self.text_fields else field
                                for field in sort_fields]
                    search = search.sort(*sort_fields)

                result = search[page_no-1:page_size].execute()
                hits += result.hits
            if hits:
                break
        max_score = max(hit.meta.score for hit in hits) if hits else 0
        response = {'total': len(hits),
                    'max_score': max_score}
        items = []
        hits.sort(key=lambda x: x.meta.score, reverse=True)
        unique_hits = set()
        for hit in hits:
            if (threshold and max_score and
                ((hit.meta.score / max_score) * 100) < threshold):
                continue
            if hit.meta.id not in unique_hits:   
                item = hit.to_dict()
                unique_hits.add(hit.meta.id)
                item.update({'_score': hit.meta.score})
                items.append(item)
        response.update({'hits': items})

        return response

    def bulk_update(self, documents):
        bulk(self.client, documents)
import json
import unittest
import requests
from aws_requests_auth.aws_auth import AWSRequestsAuth
from datetime import datetime

from requests.auth import HTTPBasicAuth


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)


class ElasticSearchResponseException(Exception):
    pass


class ElasticSearchClient(object):
    def __init__(self, **kwargs):
        self.timeout = 300
        self.base_url = kwargs.pop('base_url')
        self.auth = None

        if 'auth' in kwargs:
            auth = kwargs.pop('auth')
            if auth['type'] == 'basic':
                self.auth = HTTPBasicAuth(auth['user_name'], auth['password'])
            elif auth['type'] == 'aws':
                self.auth = AWSRequestsAuth(
                    aws_access_key=auth['aws_access_key'],
                    aws_secret_access_key=auth['aws_secret_access_key'],
                    aws_host=auth['aws_host'],
                    aws_region=auth['aws_region'],
                    aws_service=auth['aws_service']
                )

        if 'index_name' not in kwargs:
            raise Exception('Must especify index_name')

        self.index_name = kwargs.pop('index_name')

        if 'doc_type' not in kwargs:
            raise Exception('Must especify doc_type')

        self.doc_type = kwargs.pop('doc_type')

    def __process_response__(self, response):
        if not (response.status_code == 200 or response.status_code == 201):
            raise ElasticSearchResponseException('Error in elasticsearch client. Response: ' +
                                                 str(response) + ". Content: " + str(response.content))

        content_json = None
        try:
            content_json = json.loads(response.content)
        except Exception as e:
            pass

        return response, content_json

    def index(self, doc_id, doc):
        return self.__process_response__(
            requests.put("{0}/{1}/{2}/{3}".format(self.base_url, self.index_name, self.doc_type, doc_id),
                         data=json.dumps(doc, cls=CustomJSONEncoder), auth=self.auth)
        )

    def get(self, doc_id):
        return self.__process_response__(
            requests.get("{0}/{1}/{2}/{3}".format(self.base_url, self.index_name, self.doc_type, doc_id),
                         auth=self.auth)
        )

    def delete(self, doc_id):
        return self.__process_response__(
            requests.delete("{0}/{1}/{2}/{3}".format(self.base_url, self.index_name, self.doc_type, doc_id),
                            auth=self.auth)
        )

    def update(self, doc_id, doc):
        return self.__process_response__(
            requests.post("{0}/{1}/{2}/{3}/_update".format(self.base_url, self.index_name, self.doc_type, doc_id),
                          data=json.dumps(doc, cls=CustomJSONEncoder), auth=self.auth)
        )

    def search(self, query):
        return self.__process_response__(
            requests.post("{0}/{1}/_search".format(self.base_url, self.index_name),
                          data=json.dumps(query, cls=CustomJSONEncoder), auth=self.auth)
        )

    def mapping(self, mapping):
        return self.__process_response__(
            requests.post("{0}/{1}/_mapping".format(self.base_url, self.index_name),
                          data=json.dumps(mapping, cls=CustomJSONEncoder), auth=self.auth)
        )

    def build_query(self, match_list, is_and=True, sort_fields=None, params=None):
        query = {}
        for match in match_list:
            if 'bool' not in query:
                query['bool'] = {}
            if is_and:
                if 'must' not in query['bool']:
                    query['bool']['must'] = []
                query['bool']['must'].append({'match': match})
            else:
                if 'should' not in query['bool']:
                    query['bool']['should'] = []
                query['bool']['should'].append({'match': match})

        result = {
            'query': query
        }

        if params:
            page_number = params['page_number'] if 'page_number' in params else 0
            page_size = params['page_size'] if 'page_size' in params else 10
            result['from'] = page_number*page_size
            result['size'] = page_size

        if sort_fields:
            result['sort'] = map(lambda x: {x[0]: {'order': x[1]}}, map(lambda y: y, sort_fields.items()))

        return result


class TestElasticSearchClient(unittest.TestCase):
    def test_es(self):
        # test ES Client with no auth
        es_client = ElasticSearchClient(base_url="http://localhost:9200", index_name="test", doc_type="sample")
        response, content = es_client.get(1)
        self.assertTrue(response.status_code == 200)

        # test ES Client with aws auth
        es_client = ElasticSearchClient(
            base_url="https://search-es-sdp-dtv-nuaialyoz5ltpwovvnzpstazlu.us-east-1.es.amazonaws.com",
            index_name="package",
            doc_type="package",
            auth={
                'type': 'aws',
                'aws_access_key': 'AKIAIONGTGURZBEBNFBA',
                'aws_secret_access_key': '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',
                'aws_host': 'search-es-sdp-dtv-nuaialyoz5ltpwovvnzpstazlu.us-east-1.es.amazonaws.com',
                'aws_region': 'us-east-1',
                'aws_service': 'es',
            }
        )

        query = {
            "query": {
                "match": {
                    "products.provider_code": "33333333-3"
                }
            },
            "from": 0,
            "size": 10,
            "sort": [
                {
                    "timestamp": {
                        "order": "desc"
                    }
                }
            ]
        }

        response, content = es_client.search(query)
        self.assertTrue(response.status_code == 200)

if __name__ == '__main__':
    unittest.main()

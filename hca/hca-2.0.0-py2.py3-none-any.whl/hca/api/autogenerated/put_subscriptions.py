"""This file is autogenerated according to HCA api spec. Don't modify."""
from ...added_command import AddedCommand

class PutSubscriptions(AddedCommand):
    """Class containing info to reach the get endpoint of files."""

    @classmethod
    def _get_base_url(cls):
        return "https://hca-dss.czi.technology/v1"

    @classmethod
    def _get_endpoint_info(cls):
        return {u'description': u'Create a new event subscription. Every time a new bundle version matches this query,\na request is sent to callback_url.\n', u'body_params': {u'callback_url': {u'description': u'Url to send request to when a bundle comes in that matches this query.', u'format': u'url', u'hierarchy': [u'callback_url'], u'req': True, u'in': u'body', u'array': False, u'type': u'string', u'name': u'callback_url'}, u'es_query': {u'description': u'Elasticsearch query that will trigger the callback.', u'hierarchy': [u'es_query'], u'req': True, u'in': u'body', u'array': False, u'type': u'object', u'name': u'es_query'}}, u'positional': [], u'seen': False, u'requires_auth': True, u'options': {u'callback_url': {u'hierarchy': [u'callback_url'], u'in': u'body', u'description': u'Url to send request to when a bundle comes in that matches this query.', u'required_for': [u'/subscriptions'], u'format': u'url', u'pattern': None, u'array': False, u'required': True, u'type': u'string', u'metavar': None}, u'replica': {u'hierarchy': [u'replica'], u'in': u'query', u'description': u'Replica to write to. Can be one of aws, gcp, or azure.', u'required_for': [u'/subscriptions'], u'format': None, u'pattern': None, u'array': False, u'required': True, u'type': u'string', u'metavar': None}, u'es_query': {u'hierarchy': [u'es_query'], u'in': u'body', u'description': u'Elasticsearch query that will trigger the callback.', u'required_for': [u'/subscriptions'], u'format': None, u'pattern': None, u'array': False, u'required': True, u'type': u'object', u'metavar': None}}}

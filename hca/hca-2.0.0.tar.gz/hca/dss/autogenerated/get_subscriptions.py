"""This file is autogenerated according to HCA api spec. Don't modify."""
from ..added_command import AddedCommand


class GetSubscriptions(AddedCommand):
    """Class containing info to reach the get endpoint of files."""

    @classmethod
    def _get_base_url(cls):
        return "https://dss.dev.data.humancellatlas.org/v1"

    @classmethod
    def _get_endpoint_info(cls):
        return {u'description': u'Return a list of associated subscriptions, which contains the uuid,\nreplica, query, creator_uid, and callback_url.\n', u'body_params': {}, u'positional': [{u'description': u'A RFC4122-compliant ID for the subscription.', u'format': None, u'pattern': u'[A-Za-z0-9]{8}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{12}', u'required': False, u'argument': u'uuid', u'required_for': [u'/subscriptions/{uuid}'], u'type': u'string'}], u'seen': True, u'requires_auth': True, u'options': {u'replica': {u'hierarchy': [u'replica'], u'in': u'query', u'description': u'Replica to fetch from. Can be one of aws, gcp, or azure.', u'required_for': [u'/subscriptions', u'/subscriptions/{uuid}'], u'format': None, u'pattern': None, u'array': False, u'required': True, u'type': u'string', u'metavar': None}}}

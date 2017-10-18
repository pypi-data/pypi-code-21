"""This file is autogenerated according to HCA api spec. Don't modify."""
from ...added_command import AddedCommand

class GetBundles(AddedCommand):
    """Class containing info to reach the get endpoint of files."""

    @classmethod
    def _get_base_url(cls):
        return "https://hca-dss.czi.technology/v1"

    @classmethod
    def _get_endpoint_info(cls):
        return {u'description': u'Given a bundle UUID, return the latest version of that bundle.  If the version is provided, that version of the\nbundle is returned instead.\n', u'body_params': {}, u'positional': [{u'description': u'Bundle unique ID.', u'format': None, u'pattern': u'[A-Za-z0-9]{8}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{12}', u'required': True, u'argument': u'uuid', u'required_for': [u'/bundles/{uuid}'], u'type': u'string'}], u'seen': False, u'requires_auth': False, u'options': {u'version': {u'hierarchy': [u'version'], u'in': u'query', u'description': u'Timestamp of bundle creation in RFC3339.', u'required_for': [], u'format': u'date-time', u'pattern': None, u'array': False, u'required': False, u'type': u'string', u'metavar': None}, u'replica': {u'hierarchy': [u'replica'], u'in': u'query', u'description': u'Replica to fetch from.', u'required_for': [], u'format': None, u'pattern': None, u'array': False, u'required': False, u'type': u'string', u'metavar': None}, u'directurls': {u'hierarchy': [u'directurls'], u'in': u'query', u'description': u'Include direct-access URLs in the response.', u'required_for': [], u'format': None, u'pattern': None, u'array': False, u'required': False, u'type': u'boolean', u'metavar': None}}}

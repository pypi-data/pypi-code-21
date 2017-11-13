import ujson
import zlib

try:
    from zc_common.jwt_auth.utils import jwt_encode_handler
except ImportError:
    pass

from django.http import HttpRequest, QueryDict


def structure_response(status, data):
    """
    Compress a JSON object with zlib for inserting into redis.
    """
    return zlib.compress(ujson.dumps({
        'status': status,
        'body': data
    }).encode('utf-8'))


def create_django_request_object(roles, query_string, method, user_id=None, body=None, http_host=None):
    """
    Create a Django HTTPRequest object with the appropriate attributes pulled
    from the event.
    """
    if not http_host:
        http_host = 'local.zerocater.com'

    jwt_payload = {'roles': roles}
    if user_id:
        jwt_payload['id'] = user_id

    request = HttpRequest()

    # This is immediately after initializing request since setting the encoding
    #   property will delete .GET from the object
    request.encoding = 'utf-8'

    # For Django < 1.9
    request.GET = QueryDict(query_string)

    # For Django >= 1.10
    request.query_params = QueryDict(query_string)

    # For Django REST Framework >= 3.4.7
    request._read_started = False

    if body:
        request.raw_body = body

    request.method = method.upper()
    request.META = {
        'HTTP_AUTHORIZATION': 'JWT {}'.format(jwt_encode_handler(jwt_payload)),
        'QUERY_STRING': query_string,
        'HTTP_HOST': http_host,
        'CONTENT_TYPE': 'application/vnd.api+json',
        'CONTENT_LENGTH': '99999',
    }

    return request

# coding=utf-8
from sanic.response import HTTPResponse, json


"""Pre-baked, constant HTTP responses for sanic"""

# Headers
CORS_ANYWHERE = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Max-Age': 86400,
}

CACHE_FOREVER = {
    'Cache-Control': 'public, max-age=31536000',
}


# responses to posting conditions

responses = {
    'failure_not_json': {
        'info': {
            'success': False,
            'changed': False,
            'error': 'message must be json',
        },
        'http_status': 415,
    },

    'failure_invalid_json': {
        'info': {
            'success': False,
            'changed': False,
            'error': 'invalid json',
        },
        'http_status': 422,
    },

    'failure_invalid_topic': {
        'info': {
            'success': False,
            'changed': False,
            'error': 'missing or invalid hexadecimal topic',
        },
        'http_status': 422,
    },

    'failure_invalid_data': {
        'info': {
            'success': False,
            'changed': False,
            'error': 'missing or invalid base64 message data',
        },
        'http_status': 422,
    },

    'failure_invalid_signature': {
        'info': {
            'success': False,
            'changed': False,
            'error': 'invalid base64 signature',
        },
        'http_status': 422,
    },

    'failure_invalid_choke': {
        'info': {
            'success': False,
            'changed': False,
            'error': 'non-boolean choke',
        },
        'http_status': 422,
    },

    'failure_nonexistent_topic': {
        'info': {
            'success': False,
            'changed': False,
            'error': 'topic does not exist',
        },
        'http_status': 404,
    },

    'failure_unauthorized': {
        'info': {
            'success': False,
            'changed': False,
            'error': 'unauthorized signature',
        },
        'http_status': 401,
    },

    'success': {
        'info': {
            'success': True,
            'changed': True,
            'error': None,
        },
        'http_status': 201,
    },

    'nochange': {
        'info': {
            'success': True,
            'changed': False,
            'error': None,
        },
        'http_status': 200,
    },

    'failure_hash_type': {
        'info': {
            'success': False,
            'changed': False,
            'error': 'disallowed hash type',
        },
        'http_status': 422,
    },
}

http_post_responses = {
    status: json(info['info'], escape_forward_slashes=False, status=info['http_status'])
    for status, info in responses.items()
}


# OPTIONS responses

options_get = HTTPResponse(
    headers={
        'Access-Control-Allow-Methods': 'OPTIONS, GET, HEAD',
    },
    status=200,
)

options_post = HTTPResponse(
    headers={
        'Access-Control-Allow-Methods': 'OPTIONS, POST',
    },
    status=200,
)

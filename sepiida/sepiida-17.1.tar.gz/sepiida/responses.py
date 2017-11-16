import json

from flask import make_response


def json_response(data, status_code=200):
    return make_response(json.dumps(data), status_code, {'Content-Type': 'application/json'})

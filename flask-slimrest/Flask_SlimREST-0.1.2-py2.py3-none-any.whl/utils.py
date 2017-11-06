from flask import make_response, jsonify


def make_api_response(message, return_code=200):
    return make_response(jsonify(message), return_code)


def make_api_error_response(error_message, error_code=400, extra_dict_values={}):
    message = {'message': error_message}
    message.update(extra_dict_values)
    return make_api_response(message, error_code)
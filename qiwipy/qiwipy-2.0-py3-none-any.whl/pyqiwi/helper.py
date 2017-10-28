from urllib.parse import urlparse
from . import exceptions


def check_result(method_name, result):
    """
    Imported function from telebot package to check result of API Response
    :param method_name:
    :param result:
    :return:
    """
    if result.text == '':
        description = exceptions.find_exception_desc(result.status_code, method_name)
        msg = 'Error code: {0} Description: {1}'.format(result.status_code, description)
        raise exceptions.APIError(msg, method_name, response=result)
    if result.status_code != 200:
        msg = 'The server returned HTTP {0} {1}. Response body:\n[{2}]' \
            .format(result.status_code, result.reason, result.text.encode('utf8'))
        raise exceptions.APIError(msg, method_name, response=result)
    try:
        result_json = result.json()
    except:
        msg = 'The server returned an invalid JSON response. Response body:\n[{0}]' \
            .format(result.text.encode('utf8'))
        raise exceptions.APIError(msg, method_name, response=result)
    return result_json


def get_url_params(url):
    parsed_url = urlparse(url)
    params = {}
    for param in parsed_url.query.split('&'):
        params[param.split('=')[0]] = param.split('=')[1]
    return params

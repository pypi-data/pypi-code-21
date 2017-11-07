from requests import Response

from pyEchosign.exceptions.echosign import PermissionDenied
from pyEchosign.exceptions.internal import ApiError


def check_error(response):
    # type: (Response) -> None
    """ Takes a requests package response object and checks the error code and raises the proper exception """
    if response.status_code == 401:
        raise PermissionDenied('Echosign API returned a 401, your access token may be invalid if you believe your '
                               'account should have access to perform this action.')

    elif not response_success(response):
        try:
            json_response = response.json()
        except ValueError:
            json_response = ''
        raise ApiError('Received status code {} from the Echosign API with the following JSON: "{}" and content: "{}"'
                       .format(response.status_code, json_response, response.content))


def response_success(response):
    # type: (Response) -> bool
    return 199 < response.status_code < 300

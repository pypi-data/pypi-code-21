import requests


def avoid_connection_error_by_requesting_until_success(_func, *args):
    _continue = True
    while _continue:
        try:
            _res = _func(*args)
            return _res
        except requests.exceptions.SSLError or requests.exceptions.ConnectionError:
            print("Failed, trying again...")
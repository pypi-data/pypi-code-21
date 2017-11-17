import requests
import logging

log = logging.getLogger('py_piwik/helpers')

api_url = ''
api_token = ''


def _url(path: str) -> str:
    return api_url + path


def _finalize_args(args: dict, token: str, method: str) -> dict:
    args['format'] = 'JSON'
    args['module'] = 'API'
    args['token_auth'] = token
    args['method'] = method

    return args


def _process_request(url: str, args: dict):
    try:
        results = requests.get(url, params=args)
        log.debug(results.url)
    except ConnectionError as err:
        log.error(err)
        raise err
    else:
        if not results.ok:
            log.debug(results)
            raise requests.HTTPError
        return results.json()

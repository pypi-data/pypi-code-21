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

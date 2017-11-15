api_url = ''
api_token = ''


def _url(path: str) -> str:
    return api_url + path


def _finalize_args(args: dict) -> dict:
    args['format'] = 'JSON'
    args['module'] = 'API'

    return args

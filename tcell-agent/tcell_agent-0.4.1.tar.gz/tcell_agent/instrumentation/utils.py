import re


def header_keys_from_request_env(request_env):
    regex = re.compile('^HTTP_')
    headers = list(regex.sub('', header) for (header, value)
                   in request_env.items() if
                   header.startswith('HTTP_') or header == "CONTENT_TYPE" or header == "CONTENT_LENGTH")
    return headers


STATUS_CODE_OK = '200 OK'
STATUS_CODE_ACCEPTED = '202 Accepted'
STATUS_CODE_BAD_REQUEST = '400 Bad Request'
STATUS_CODE_NOT_FOUND = '404 Not Found'
STATUS_CODE_EXCEPTION_FAILED = '417 Expectation Failed'
STATUS_CODE_UNAUTHORIZED = '401 Unauthorized'


def create_url_regex(url_name, trail_num=None):
    """
    Used to create the API
    :param url_name: The origin url name
    :param trail_num: Number of trails URL to disregard: (XXX/XXX/XXX)
    :return:
    """
    url = "/" + url_name
    if trail_num:
        for i in range(trail_num):
            url += "/([%&+ \w]+)"
    return url + ".*"


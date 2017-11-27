
def get_paginated_response(session, url, params={}, **kwargs):
    """
    Get the results of all pages of a response. Returns an iterator
    that returns each of the items.
    """
    while url is not None:
        data = session.get(url, params=params, **kwargs)
        for result in data.get('results', []):
            yield result
        url = data.get('next', None)
        if url is not None:
            # We remove part of the url that the session already has
            url = url.replace(session.url, '')
        # params are included in the next url
        params = {}

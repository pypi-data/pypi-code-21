import urlparse

def make_url(scheme, host, path):
    # URL's host shouldn't contain any '/' characters. If it does, throw
    if '/' in host:
        raise Exception("URL host contains one or more '/' characters")

    url_parts = [
        scheme,
        host,
        path,
        '', '', ''
    ]
    return urlparse.urlunparse(url_parts)

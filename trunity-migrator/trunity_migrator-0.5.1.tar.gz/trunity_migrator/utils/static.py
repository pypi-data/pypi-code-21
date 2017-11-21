from urllib.parse import urljoin, urlsplit, urlparse


def url_repair(url: str, url_base: str) -> str:
    """
    Takes url and append base to it if needed.
    url_base is something like 'http://netloc.com' etc..

    :param url:
    :param url_base:
    :return:
    """
    url_split = urlsplit(url)

    if url_split.scheme:
        return url
    else:
        return urljoin(url_base, url)

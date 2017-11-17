from __future__ import unicode_literals, absolute_import


def local_ip():
    '''get local ip address for IP V4

    Returns:
        string: current machine ip

    TODO:
        ip v6 not implement
    '''

    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 0))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


def html(url, **kwargs):
    '''get html string object by url

    User-Agent :
        default "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:52.0) Gecko/20100101 Firefox/52.0"
        modify User-Agent put to headers in kwargs

    Args:
        * url (string): requested http url
        * kwargs
        * timeout : set get timeout default 60
        * headers : set http headers have User-Agent
        * params : set http parameters
        * retry : set retry count default 0
        * encoding : page encoding default utf8
        * method : set http method default get
        * json : if True return json else return string

    Returns:
        string: if request correct else None
    '''

    from dandan import value
    import requests
    # import traceback

    kwargs = value.AttrDict(kwargs)
    timeout = kwargs.timeout or 60
    headers = kwargs.headers or value.AttrDict()
    params = kwargs.params or value.AttrDict()
    method = kwargs.method or 'get'
    retry = kwargs.retry or 0
    encoding = kwargs.encoding or "utf8"
    json = kwargs.json or False

    user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:52.0) Gecko/20100101 Firefox/52.0"
    headers["User-Agent"] = headers["User-Agent"] or user_agent

    for _ in range(0, retry + 1):
        try:
            if method.lower() == 'post':
                res = requests.post(url, data=params.dict(), headers=headers, timeout=timeout)
            else:
                res = requests.get(url, params=params, headers=headers, timeout=timeout)
            res.encoding = encoding
            if json:
                return res.json()
            return res.text
        except Exception:
            continue

    return None


def soup(url, **kwargs):
    '''get BeautifulSoup object by url

    Args:
        * url (string): requested http url
        * \*\*kwargs: same as :py:func:`html`

    Returns:
        BeautifulSoup: if request correct else None
    '''

    from bs4 import BeautifulSoup as bs
    text = html(url, **kwargs) or ""
    return bs(text, "html.parser")


def json(url, **kwargs):
    '''get json object by url familiar html if http return json or None

    Args:
        * url (string): requested http url
        * \*\*kwargs: same as :py:func:`html`

    Returns:
        json: if request correct else None
    '''
    return html(url, json=True, **kwargs)


def whois(ip):
    """
    Get whois infommation (developing)

    Args:
        * ip (string): request for whois

    Returns:
        * AttrDict: if get whois currect else None
    """
    import value

    result = value.AttrDict()
    result.ip = ip

    api = "http://freegeoip.net/json/{}".format(ip)
    res = json(api, timeout=5)
    if not res:
        return result

    res = value.AttrDict(res)

    result.region = res.region_name
    return result

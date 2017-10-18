import tornado.httpclient
import urllib


async def async_fetch_url(
        url, method='GET', headers={}, raise_error=False, **params):
    if method not in ('GET', 'POST', 'PATCH', 'PUT', 'DELETE'):
        return None
    request = None
    headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
    if method == 'GET':
        request = tornado.httpclient.HTTPRequest(
            str.format('{url}?{params}',
                       url=url,
                       headers=headers,
                       params=urllib.parse.urlencode(params)))
    else:
        request = tornado.httpclient.HTTPRequest(
            str.format('{url}', url=url),
            headers=headers,
            body=urllib.parse.urlencode(params),
            method=method)
    client = tornado.httpclient.AsyncHTTPClient()
    response = await client.fetch(request, raise_error=raise_error)
    return response


def fetch_url(url, method='GET', headers={}, **params):
    if method not in ('GET', 'POST', 'PATCH', 'PUT', 'DELETE'):
        return None
    request = None
    headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
    if method == 'GET':
        request = tornado.httpclient.HTTPRequest(
            str.format('{url}?{params}',
                       url=url,
                       headers=headers,
                       params=urllib.parse.urlencode(params)))
    else:
        request = tornado.httpclient.HTTPRequest(
            str.format('{url}', url=url),
            headers=headers,
            body=urllib.parse.urlencode(
                params) if method is not 'DELETE' else None,
            method=method)
    client = tornado.httpclient.HTTPClient()
    response = client.fetch(request, raise_error=False)
    return response

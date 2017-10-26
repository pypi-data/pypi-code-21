def url_format(host, port, url, method="http"):
    return "{method}://{host}:{port}{url}".format(method=method, host=host, port=port, url=url)

class Resource(object):
    '''
    Base class for all resources.
    '''

    def __init__(self, resource_url, http_client):
        self._http_client = http_client
        self._resource_url = resource_url

    def rurl(self, rel_path=None):
        if rel_path:
            return '%s/%s' % (self._resource_url, rel_path)
        else:
            return self._resource_url

    def get(self, path, params=None, endpoint=None, headers=None, raw=False):
        return self._http_client.get(path, params, endpoint,
                                     headers, raw)

    def post(self, path, params=None, data=None, endpoint=None, headers=None,
             raw=False):
        return self._http_client.post(path, params, data,
                                      endpoint, headers, raw)

    def put(self, path, params=None, data=None, endpoint=None, headers=None,
            raw=False):
        return self._http_client.put(path, params, data,
                                     endpoint, headers, raw)

    def delete(self, path, params=None, endpoint=None, headers=None,
               raw=False):
        return self._http_client.delete(path, params, endpoint,
                                        headers, raw)

import requests


class Session(requests.Session):
    def __init__(self, encoding='', timeout=0):
        super().__init__()
        self._encoding = encoding
        self._timeout = timeout

    def get(self, url, **kwargs):
        self._setup_kwargs(kwargs)
        r = super().get(url, **kwargs)
        r.raise_for_status()
        if self._encoding:
            r.encoding = self._encoding
        return r

    def post(self, url, data=None, json=None, **kwargs):
        self._setup_kwargs(kwargs)
        r = super().post(url, data, json, **kwargs)
        r.raise_for_status()
        r.encoding = self._encoding
        return r

    def _setup_kwargs(self, kwargs):
        if self._timeout and 'timeout' not in kwargs:
            kwargs['timeout'] = self._timeout

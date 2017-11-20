from abc import ABCMeta

from requests import Session, Request
from requests.cookies import RequestsCookieJar

from cobweb.adapters import AbstractAdapter
from cobweb.bbs import BlockBypassSystem


class SessionAbstractAdapter(AbstractAdapter, metaclass=ABCMeta):

    bbs = BlockBypassSystem()

    def __init__(
            self,
            use_bbs=True,
            method="GET",
            stream=False,
            proxies=None,
            ssl_certificate=None,
            keep_session=True,
            timeout=(10, 10),
            data=None,
            headers=None):

        if not use_bbs:
            self.bbs.stop()

        self._use_bbs = use_bbs
        self._headers = {"User-Agent": "Python-Cobweb/1.0.0"}
        if headers:
            self.headers.update(**headers)
        self._data = data
        self._timeout = timeout
        self._ssl_certificate = ssl_certificate
        self._proxies = proxies
        self._method = method
        self._stream = stream
        self._response = None
        self._content = None
        self._cookies = None
        self.session = Session() if keep_session else None
        self.accept_content_types = {}

    @property
    def use_bbs(self):
        return self._use_bbs

    @property
    def logger(self):
        raise ValueError("Called logger on an abstract class")

    @property
    def headers(self) -> dict:
        return self._headers

    @property
    def cookies(self) -> RequestsCookieJar:
        return self._cookies

    @use_bbs.setter
    def use_bbs(self, value):
        self._use_bbs = value
        if not value:
            self.bbs.stop()
        else:
            self.bbs.start()

    def __enter__(self):
        self.session = Session()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_session()

    def invoke(self, url: str):
        if not self.session:
            self.logger.debug("open session")
            self.session = Session()
            response = self.send(url)
            self.close_session()
        else:
            response = self.send(url)
        return response

    def close_session(self):
        self.session.close()
        self.session = None
        self.logger.debug("session closed")

    def send(self, url: str):
        self.logger.debug("enter session")
        with self.session as session:
            response = session.send(
                self.prepare_request(url),
                stream=self._stream,
                verify=self._ssl_certificate,
                proxies=self._proxies,
                cert=self._ssl_certificate,
                timeout=self._timeout
            )
        self.logger.debug("got response")
        return self.process_response(response)

    @bbs.monitor_requests
    def prepare_request(self, url: str):
        self.logger.debug("preparing request")
        request = Request(self._method, url, data=self._data, headers=self._headers)
        self._cookies = request.cookies
        return self.session.prepare_request(request)

    def process_response(self, response):
        if ";" in response.headers["content-type"]:
            response.headers["content-type"] = response.headers["content-type"].partition(";")[0]
        return response

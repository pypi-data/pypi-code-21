import logging

from requests import Request, Session
from requests.cookies import RequestsCookieJar
from requests.exceptions import HTTPError

from cobweb.adapters import AbstractAdapter


class Http(AbstractAdapter):

    def __init__(
            self,
            method="GET",
            stream=False,
            proxies=None,
            ssl_certificate=None,
            timeout=(10, 10),
            data=None,
            headers=None):

        self._headers = headers
        self._data = data
        self._timeout = timeout
        self._ssl_certificate = ssl_certificate
        self._proxies = proxies
        self._method = method
        self._stream = stream
        self._response = None
        self._content = None
        self.session = None
        self.accept_content_types = {
            "text/html",
            "text/plain",
            "application/xhtml+xml",
            "application/xml",
        }

    @property
    def logger(self):
        return logging.getLogger("cobweb.adapters.http")

    @property
    def headers(self) -> dict:
        return self._headers

    @property
    def cookies(self) -> RequestsCookieJar:
        return self._cookies

    def __enter__(self):
        self.session = Session()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_session()

    def __str__(self) -> str:
        return "Http response status {}: \n{}".format(self.status_code, self.content.body)

    def __call__(self, url: str):
        if not self.session:
            self.session = Session()
            response = self.send(url)
            self.close_session()
        else:
            response = self.send(url)
        return response

    def close_session(self):
        self.session.close()
        self.session = None

    def send(self, url: str):
        self.logger.debug("open session")
        with self.session as s:
            response = s.send(
                self.prepare_request(url),
                stream=self._stream,
                verify=self._ssl_certificate,
                proxies=self._proxies,
                cert=self._ssl_certificate,
                timeout=self._timeout
            )
        self.logger.debug("got response")
        return self.process_response(response)

    def prepare_request(self, url: str):
        self.logger.debug("preparing request")
        request = Request(self._method, url, data=self._data, headers=self._headers)
        return self.session.prepare_request(request)

    def process_response(self, response):
        if response.headers["content-type"].partition(";")[0] not in self.accept_content_types:
            raise HTTPError("Wrong content type")
        return response


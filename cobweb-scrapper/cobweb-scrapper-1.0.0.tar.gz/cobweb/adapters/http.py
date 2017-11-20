import logging

from bs4 import BeautifulSoup
from requests import HTTPError

from cobweb.adapters.session import SessionAbstractAdapter
from cobweb.bbs import BlockBypassSystem


class HttpAdapter(SessionAbstractAdapter):

    bbs = BlockBypassSystem()

    def __init__(self, **kwargs):

        super(HttpAdapter, self).__init__(**kwargs)

        self.accept_content_types = {
            "text/html",
            "text/plain",
            "application/xhtml+xml",
            "application/xml",
        }

    @property
    def logger(self):
        return logging.getLogger("cobweb.adapters.http")

    @bbs.monitor_responses
    def process_response(self, response):
        response = super().process_response(response)

        if response.headers["content-type"] not in self.accept_content_types:
            raise HTTPError("Wrong content type")

        response.processed_by = self.__class__
        response.data = BeautifulSoup(response.content, "html.parser")
        return response

import logging
from io import BytesIO

from cobweb.adapters.session import SessionAbstractAdapter
from cobweb.bbs import BlockBypassSystem


class FileAdapter(SessionAbstractAdapter):

    bbs = BlockBypassSystem()

    def __init__(self, **kwargs):
        super(FileAdapter, self).__init__(**kwargs)

    @property
    def logger(self):
        return logging.getLogger("cobweb.adapters.file")

    @bbs.monitor_responses
    def process_response(self, response):
        response = super().process_response(response)
        response.processed_by = self.__class__

        response.data = BytesIO(response.content)
        return response

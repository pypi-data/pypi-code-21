from PIL import Image

from cobweb.adapters.file import FileAdapter
from cobweb.bbs import BlockBypassSystem


class ImageAdapter(FileAdapter):

    bbs = BlockBypassSystem()

    @bbs.monitor_responses
    def process_response(self, response):
        response = super().process_response(response)
        response.processed_by = self.__class__

        response.data = Image.open(response.data)
        return response

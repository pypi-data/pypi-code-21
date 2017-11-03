
import logging_helper
from .base import BaseRequestHandler


logging = logging_helper.setup_logging()


class GetHandler(BaseRequestHandler):

    METHOD_TYPE = u'GET'

    def __init__(self,
                 *args,
                 **kwargs):
        super(GetHandler, self).__init__(*args, **kwargs)

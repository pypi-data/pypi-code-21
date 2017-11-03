
import cgi
import logging_helper
from .base import BaseRequestHandler


logging = logging_helper.setup_logging()


class PostHandler(BaseRequestHandler):

    METHOD_TYPE = u'POST'

    def __init__(self,
                 *args,
                 **kwargs):
        super(PostHandler, self).__init__(*args, **kwargs)

    def extract_parameters(self):

        # TODO: Test against Form submission
        # (Only tried with JSON)

        # try:
        #     form = cgi.FieldStorage(
        #         fp=self.rfile,
        #         headers=self.headers,
        #         environ={u'REQUEST_METHOD': u'POST',
        #                  u'CONTENT_TYPE':   self.headers[u'Content-Type'],
        #                  })
        #     logging.warning(u"======= POST VALUES =======")
        #     if form.list:
        #         for item in form.list:
        #             logging.warning(item)
        #     logging.warning(u"\n")
        # except:
        #     pass

        content_length = int(self._request.headers.getheader(u'content-length', -1))
        if content_length != -1:
            body = self._request.rfile.read(content_length)
        else:
            body = self._request.rfile.read()  # read all??

        self._request.parameters = {u'data': body}

        logging.info(u'POST data:{body}'.format(body=body))

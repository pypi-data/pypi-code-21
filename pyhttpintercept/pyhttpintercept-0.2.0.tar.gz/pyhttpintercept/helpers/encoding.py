
import logging_helper
from .compression import compress, CMP_METHODS

logging = logging_helper.setup_logging()

USE_REMOVE_ENCODING_HACK = False


def _remove_content_encoding_header(response):

    if u'content-encoding' in response.headers:
        logging.warning(u'removing content-encoding:{ce}'.format(ce=response.headers[u'content-encoding']))

        del response.headers[u'content-encoding']


def encode_response(content,
                    encoding):

    if encoding in (u'gzip', u'x-gzip', u'deflate'):
        logging.debug(u'Response encoding for {encoding}'.format(encoding=encoding))

        return compress(content, CMP_METHODS.zlib if encoding == u'deflate' else CMP_METHODS.gzip)

    logging.debug(u'Response content unchanged for encoding {encoding}!'.format(encoding=encoding))

    return content


def encode_requests_response(response):

    if USE_REMOVE_ENCODING_HACK:
        _remove_content_encoding_header(response)

    else:
        response._content = encode_response(content=response.content,
                                            encoding=response.headers.get(u'content-encoding', None))

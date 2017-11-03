# encoding: utf-8

u"""
==================================================================================
This function forces the configured status code in the HTTP response,
----------------------------------------------------------------------------------
Filter     : A string to match in the request.
             Leave blank to modify for all requests.
Override   : N/A
Parameters : Code from below Example HTTP Errors
             Leave blank for a default is 400
             Value must be an integer
----------------------------------------------------------------------------------
100: ('Continue', 'Request received, please continue'),
101: ('Switching Protocols',
      'Switching to new protocol; obey Upgrade header'),
200: ('OK', 'Request fulfilled, document follows'),
201: ('Created', 'Document created, URL follows'),
202: ('Accepted',
      'Request accepted, processing continues off-line'),
203: ('Non-Authoritative Information', 'Request fulfilled from cache'),
204: ('No Content', 'Request fulfilled, nothing follows'),
205: ('Reset Content', 'Clear input form for further input.'),
206: ('Partial Content', 'Partial content follows.'),
300: ('Multiple Choices',
      'Object has several resources -- see URI list'),
301: ('Moved Permanently', 'Object moved permanently -- see URI list'),
302: ('Found', 'Object moved temporarily -- see URI list'),
303: ('See Other', 'Object moved -- see Method and URL list'),
304: ('Not Modified',
      'Document has not changed since given time'),
305: ('Use Proxy',
      'You must use proxy specified in Location to access this '
      'resource.'),
307: ('Temporary Redirect',
      'Object moved temporarily -- see URI list'),
400: ('Bad Request',
      'Bad request syntax or unsupported method'),
401: ('Unauthorized',
      'No permission -- see authorization schemes'),
402: ('Payment Required',
      'No payment -- see charging schemes'),
403: ('Forbidden',
      'Request forbidden -- authorization will not help'),
404: ('Not Found', 'Nothing matches the given URI'),
405: ('Method Not Allowed',
      'Specified method is invalid for this resource.'),
406: ('Not Acceptable', 'URI not available in preferred format.'),
407: ('Proxy Authentication Required', 'You must authenticate with '
      'this proxy before proceeding.'),
408: ('Request Timeout', 'Request timed out; try again later.'),
409: ('Conflict', 'Request conflict.'),
410: ('Gone',
      'URI no longer exists and has been permanently removed.'),
411: ('Length Required', 'Client must specify Content-Length.'),
412: ('Precondition Failed', 'Precondition in headers is false.'),
413: ('Request Entity Too Large', 'Entity is too large.'),
414: ('Request-URI Too Long', 'URI is too long.'),
415: ('Unsupported Media Type', 'Entity body in unsupported format.'),
416: ('Requested Range Not Satisfiable',
      'Cannot satisfy request range.'),
417: ('Expectation Failed',
      'Expect condition could not be satisfied.'),
500: ('Internal Server Error', 'Server got itself in trouble'),
501: ('Not Implemented',
      'Server does not support this operation'),
502: ('Bad Gateway', 'Invalid responses from another server/proxy.'),
503: ('Service Unavailable',
      'The server cannot process the request due to a high load'),
504: ('Gateway Timeout',
      'The gateway server did not receive a timely response'),
505: ('HTTP Version Not Supported', 'Cannot fulfill request.')
==================================================================================
"""

import logging_helper
from BaseHTTPServer import BaseHTTPRequestHandler

logging = logging_helper.setup_logging()


def modify(request,
           response,
           parameters):

    if parameters.passes_filter(value=request,
                                wildcards=u''):

        # Setup parameters
        try:
            code = parameters.params
            code = int(code)
        except KeyError:
            logging.info(parameters)
            code = 400
        except ValueError:
            logging.error(u'Bad code value. Aborting modifier.')
            return response

        logging.info(u'HTTP status code is set to: {code}'.format(code=code))

        # Reply to client with error response
        response.status_code = code
        if BaseHTTPRequestHandler.responses.get(code):
            response._content = (u'<h1>{short}</h1>\n'
                                 u'<p>{long}</p>'.format(short=BaseHTTPRequestHandler.responses[code][0],
                                                         long=BaseHTTPRequestHandler.responses[code][1]))
        else:
            response._content = (u'<h1>Dummy Error Response</h1>'
                                 u'<p>you entered either an invalid '
                                 u'or unaccounted for error code!</p>')

        response.headers = {u'Content-Type': u'text/html',
                            u'content-length': len(response.content)}

    return response

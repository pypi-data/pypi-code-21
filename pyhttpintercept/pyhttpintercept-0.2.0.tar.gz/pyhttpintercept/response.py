# encoding: utf-8

import logging_helper
import six
from requests.models import Response as _Resp
from requests.structures import CaseInsensitiveDict
from BaseHTTPServer import BaseHTTPRequestHandler
from .helpers.encoding import encode_requests_response

logging = logging_helper.setup_logging()


class Response(object):

    def __init__(self,
                 request,
                 uri=None,
                 response=None):

        """
        
        :param request:     The original request object
        :param response:    Optionally provide a requests.Response object that will be 
                            used to initialise this object
        """

        self._request = request
        self.canned_responses = BaseHTTPRequestHandler.responses

        self.client_address = request.client_address

        self.request_uri = (uri
                            if uri is not None
                            else u'http://{host_port}{path}'.format(host_port=request.headers[u'Host'],
                                                                    path=request.path))

        # Response parameters
        if response is not None and isinstance(response, _Resp):
            # Initialise response from requests.Response object
            encode_requests_response(response)

            self.headers = response.headers
            self.content = response.content
            self.status = response.status_code

        else:
            # Initialise with defaults
            self.headers = {u'content-length': 0}
            self.content = None
            self.status = 200  # Start with a good status, any errors will modify this!

    def generate_error(self,
                       err,
                       status=500):  # Internal server error

        # Setup error response
        self.status = status
        self.content = u''

        # Check if we can get a defined description for failure.
        if self.canned_responses.get(self.status):
            self.content += (u'<h1>{short}</h1>'
                             u'<p>{long}:</p>'.format(short=self.canned_responses[self.status][0],
                                                      long=self.canned_responses[self.status][1]))

        self.content += (u'<pre>{err}</pre>'.format(err=err))

        # Headers must be last so we generate correct content length!
        self.headers = {u'Content-Type': u'text/html',
                        u'Connection': u'close',
                        u'content-length': len(self.content)}

    def prepare_headers(self,
                        modified_headers=None):

        if modified_headers is None:
            modified_headers = {}  # Initalise modifier_headers if not provided

        # Push the modified headers to a case insensitive dict so that
        # the case does not have to be checked when fetching from
        # the dictionary
        modified_headers = CaseInsensitiveDict(data=modified_headers)

        logging.debug(u'Modified headers: {h}'.format(h=modified_headers))

        # Check for and remove chunked transfer encoding
        for header in self.headers.keys():
            if header.lower() == u'transfer-encoding' and u'chunked' in self.headers[header]:
                logging.debug(u'Removing chunked transfer-encoding')
                del self.headers[header]

        # Update headers
        for header in self.headers:
            # Update for any modified headers
            # Content length must be handled separately!
            if self.content is not None and header.lower() == u'content-length':
                # Check modified_headers for overridden content-length
                if not header.lower() in [h.lower() for h in modified_headers]:
                    logging.info(u'Updating content-length to reflect any modifications '
                                 u'to content ({o} -> {l}).'.format(o=self.headers[header],
                                                                    l=len(self.content)))

                # Check for overridden header content length,
                # otherwise send correct length
                value = modified_headers.get(header, len(self.content))

            else:
                # Check if header is one of the modified,
                # --> If yes: use the modified header
                # --> If no: use the original header
                value = modified_headers.get(header, self.headers.get(header))

            self.headers[header] = value

    def __send_headers(self):

        # Send the headers
        for header, value in six.iteritems(self.headers):

            logging.debug(u'Sending header ({header}:{value})'.format(header=header,
                                                                      value=value))
            try:
                self._request.send_header(header, value)

            except Exception as err:
                logging.error(u'Error sending header ({header}:{value}) to {client} for {url}!  '
                              u'Client may not handle response correctly!'.format(header=header,
                                                                                  value=value,
                                                                                  client=self.client_address,
                                                                                  url=self.request_uri))
                logging.error(err)

        # Notify end of headers
        try:
            logging.debug(u'Sending end headers for response')
            self._request.end_headers()

        except Exception as err:
            logging.exception(u'Error sending end headers for response')
            raise err

    def respond(self):

        # This Sends the response code plus Server & Date headers
        logging.debug(u'Sending status ({s})'.format(s=self.status))
        self._request.send_response(self.status)

        # Send our response headers including the "End Header" message
        self.__send_headers()

        # Check whether we should send content body
        # --> HEAD requests expect no body
        # --> only send if status code is 200 or above
        # --> do not send if status code is 204 (No Content) or 304 (Not Modified)
        if self._request.command.upper() != u'HEAD' and self.status >= 200 and self.status not in (204, 304):

            try:
                # Send content body
                logging.debug(u'Sending content')
                self._request.wfile.write(str(self.content))

            except Exception as err:
                logging.exception(u'Error sending response content')
                raise err

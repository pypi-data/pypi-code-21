# encoding: utf-8

import threading
import logging_helper
from ..response import Response
from ..config.hosting import Sites

logging = logging_helper.setup_logging()


class HostRequest(object):

    def __init__(self,
                 request,
                 uri=None):

        self._request = request
        self.response = Response(request=self._request)

        self.client_address = request.client_address

        self.request_uri = (uri
                            if uri is not None
                            else u'http://{host_port}{path}'.format(host_port=request.headers[u'Host'],
                                                                    path=request.path))

        uri = self.request_uri.split(u'://')[1]
        host, path = uri.split(u'/', 1)

        self.request_host = host
        self.request_path = u'/{path}'.format(path=path)

        self.hosted = False

    @property
    def thread(self):
        thread = threading.currentThread().name
        return thread if thread else u'?'

    def prefix_message(self,
                       msg):
        return u'HTTP {type} ({thread}): {msg}'.format(type=self._request.command.upper(),
                                                       thread=self.thread,
                                                       msg=msg)

    def _get_debug_separator(self,
                             section):
        return self.prefix_message(u'=========================== '
                                   u'{section} '
                                   u'==========================='.format(section=section))

    # Error processing
    def __handle_error(self,
                       err,
                       status=500,  # Internal server error
                       log_msg=u'Something went wrong!'):

        # Log the error
        logging.error(self.prefix_message(log_msg))
        logging.exception(self.prefix_message(err))

        # Setup error response
        self.response.generate_error(err=err,
                                     status=status)

    # Hosting
    def host_request(self):

        try:
            # Check is site is configured
            site = Sites().get_item(self.request_path,
                                    active_only=True)

            # If we haven't raised a LookupError then site is configured to host the request
            self.__handle_host_request(site)

        except LookupError:
            # Check for server test page
            if self.request_path == u'/test':
                self.__server_test_page()

            # No sites or static pages found.
            else:
                logging.debug(self.prefix_message(u'Not Hosting this request, '
                                                  u'path is either disabled or not configured.'))

        return self.response, self.hosted

    def __handle_host_request(self,
                              site):
        logging.debug(self._get_debug_separator(u'HOST REQUEST'))

        logging.debug(self.prefix_message(site.doc_root))

        # TODO: Need to handle serving the hosted site here
        # Start by handling the index.html
        # Once that is working we should look at decoding sub pages within the site!

        # ### Temporary response! ###
        msg = u'Hosting is not yet supported on this server! ({url})'.format(url=self.request_uri)
        self.__handle_error(err=msg,
                            status=501,  # Not Implemented
                            log_msg=msg)
        # ### End temporary response ###

        self.hosted = True  # Flag that the request has been hosted

        logging.debug(self._get_debug_separator(u'END HOST REQUEST'))

    def __server_test_page(self):

        logging.debug(self._get_debug_separator(u'SERVER TEST PAGE'))

        # Prepare response
        self.response.content = (u'<h1>Server Test Page</h1>'
                                 u'<p>you have requested {uri}</p>'
                                 u'<pre>Congratulations the server is working!</pre>'
                                 .format(uri=self.request_uri))

        self.response.status = 200
        self.response.headers = {u'Content-Type': u'text/html',
                                 u'content-length': len(self.response.content)}

        self.hosted = True  # Flag that the request has been hosted

        logging.debug(self._get_debug_separator(u'END SERVER TEST PAGE'))

# encoding: utf-8

import requests
import threading
import logging_helper
from pydnserver import dns_lookup
from networkutil.addressing import get_my_addresses
from ..response import Response
from ..hosting import HostRequest
from ..intercept import InterceptRequest
from ..exceptions import CircularReference

logging = logging_helper.setup_logging()


class BaseRequestHandler(object):

    METHOD_TYPE = None  # This should be set by inheriting class

    def __init__(self,
                 request,
                 scenarios=None):

        self._request = request

        self._scenarios = scenarios

        self.client_address = request.client_address

        # Save the request parameters
        self.request_headers = request.headers
        self.request_host = self.request_headers[u'Host']
        self.request_path = request.path

        # Processing parameters
        self.retrieved_headers = {}
        self.modified_headers = {}

        # Create the response object
        self.response = Response(request=self._request)

        # handler flags
        self.hosted = False
        self.intercepted = False
        self.proxied = False

    # Properties
    @property
    def _request_address(self):
        return self.request_host.split(u':')[0]

    @property
    def _addressed_to_self(self):
        return self._request_address in get_my_addresses()
        # TODO: Add ability to configure & check server aliases

    @property
    def request_uri(self):
        return u'http://{host_port}{path}'.format(host_port=self.request_host,
                                                  path=self.request_path)

    @request_uri.setter
    def request_uri(self, value):

        uri = value.split(u'://')[1]
        host, path = uri.split(u'/', 1)

        self.request_host = host
        self.request_path = u'/{path}'.format(path=path)

    @property
    def thread(self):
        thread = threading.currentThread().name
        return thread if thread else u'?'

    # Log message formatters
    def prefix_message(self,
                       msg):
        return u'HTTP {type} ({thread}): {msg}'.format(type=self.METHOD_TYPE.upper(),
                                                       thread=self.thread,
                                                       msg=msg)

    def _get_debug_separator(self,
                             section):
        return self.prefix_message(u'=========================== '
                                   u'{section} '
                                   u'==========================='.format(section=section))

    def extract_parameters(self):
        self._request.parameters = {}

    # Interface
    def handle(self):

        # logging.debug(self._get_debug_separator(u'REQUEST'))
        # logging.debug(self.prefix_message(u'Headers - \n{h}'.format(h=self.request_headers)))
        # logging.debug(self.prefix_message(u'Client - {h}'.format(h=self.client_address)))

        try:
            self.extract_parameters()

            self.__redirect_request()

            # Attempt to host the request
            self.__host_request()

            if not self.hosted:
                # Attempt to intercept the request only if not already hosted
                self.__intercept_request()

            if not self.hosted and not self.intercepted:
                # Attempt to proxy the request only if not already hosted or intercepted
                self.__proxy_request()

        except CircularReference as err:
            self.__handle_error(err=err,
                                status=400,
                                log_msg=str(err))

        except requests.exceptions.RequestException as err:
            self.__handle_error(err=err,
                                status=408,  # Request Timeout  # TODO: Careful this might not always be a timeout!
                                log_msg=u'Request to {url} failed'.format(url=self.request_uri))

        except Exception as err:
            self.__handle_error(err=err)  # Uses default status - 500: Internal server error

        finally:
            # Reply to client with response
            self.response.respond()

        # logging.debug(self._get_debug_separator(u'END REQUEST'))

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

    # Request handlers  TODO: Wildcard support
    # Redirect TODO: This needs writing, current content is old method brought forward for time being
    def __redirect_request(self):

        # TODO: We should remove dependency on dns config for redirects and use our own custom config!

        try:
            # Do we need to redirect?
            # this will return the redirect hostname if configured in the DNS config
            self.request_host = dns_lookup.get_redirect_hostname_for_host(self.request_host)

        except dns_lookup.NoActiveRecordForHost:
            pass

        logging.debug(self.prefix_message(self.request_host))

    # Hosting
    def __host_request(self):

        # Only host the request when it is addressed directly to the server
        if self._addressed_to_self:
            host = HostRequest(request=self._request,
                               uri=self.request_uri)

            # TODO: should we be setting response if hosted comes back False?
            self.response, self.hosted = host.host_request()

        else:
            pass
            #logging.debug(self.prefix_message(u'Not Hosting this request, Request not addressed to this server.'))

    # Intercept
    def __intercept_request(self):

        if self._scenarios is not None:
            intercept = InterceptRequest(request=self._request,
                                         scenarios=self._scenarios,
                                         uri=self.request_uri)

            # TODO: should we be setting response if intercepted comes back False?
            self.response, self.intercepted = intercept.intercept_request()

        else:
            pass
            # logging.warning(u'Intercept is disabled as self._scenarios is None!')

    # Proxy TODO
    def __proxy_request(self):

        # TODO: Check for configured proxy
        proxy = False

        if proxy:
            # Get real response from server
            response = requests.get(url=self.request_uri,
                                    timeout=1.5)
            # TODO: need to forward headers & query params also!

            # Prepare response
            self.response = Response(request=self._request,
                                     uri=self.request_uri,
                                     response=response)
            self.response.prepare_headers()

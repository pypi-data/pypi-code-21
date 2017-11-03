# encoding: utf-8

import copy
import socket
import requests
import threading
import logging_helper
from networkutil.addressing import get_my_addresses
from networkutil.endpoint_config import Endpoints
from ..response import Response
from ..config.constants import HandlerConstant, ModifierConstant, HandlerTypeConstant
from ..exceptions import NoHandlersFound, NoActiveModifiers, CircularReference

logging = logging_helper.setup_logging()


class InterceptRequest(object):

    def __init__(self,
                 request,
                 scenarios,
                 uri=None):

        self._request = request
        self._scenarios = scenarios

        # make handlers & modifiers easier to access
        self._handlers = self._scenarios.handlers
        self._modifiers = self._scenarios.modifiers

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

        self.intercepted = False

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

    # Intercept
    def intercept_request(self):

        #  Make Modifications to URI
        #  TODO: part of this functionality should be moved to redirect request handler
        logging.info(self.prefix_message(u'Original URI: {uri}'.format(uri=self.request_uri)))

        modified_uri = self.__modify(response=None,
                                     kind=HandlerTypeConstant.uri,
                                     separator=u'MODIFY URI')

        modified_uri = modified_uri if modified_uri is not None else self.request_uri

        if modified_uri != self.request_uri:
            self.request_uri = modified_uri
            logging.info(self.prefix_message(u'Modified URI: {uri}'.format(uri=self.request_uri)))

        # Check for and get canned response
        #  TODO: this functionality should be moved to hosting request handler!
        response = self.__modify(response=None,
                                 kind=HandlerTypeConstant.canned,
                                 separator=u'CHECK FOR CANNED RESPONSE')

        # Get a real response if there is no canned response configured
        if response is None:
            response = self.__make_actual_request()

        # Make Modifications to response
        modified_response = self.__modify(response=response,
                                          kind=HandlerTypeConstant.body,
                                          separator=u'MODIFY RESPONSE')

        response = modified_response if modified_response is not None else response

        # Make Modifications to headers
        # logging.info(self.prefix_message(u'Original Headers: {h}'.format(h=response.headers)))

        modified_headers = self.__modify(response=response,
                                         kind=HandlerTypeConstant.header,
                                         separator=u'HEADER')

        # Prepare response
        self.response = Response(request=self._request,
                                 uri=self.request_uri,
                                 response=response)
        self.response.prepare_headers(modified_headers=modified_headers if modified_headers is not None else {})

        return self.response, self.intercepted

    def __make_actual_request(self):

        # Ensure request is not circular!
        host = self.request_host.split(u':')[0]
        try:
            host_address = socket.gethostbyname(host)
        except socket.gaierror as e:
            logging.exception(u'Could not resolve {host} to an address. '
                              u'The address may not be available on this interface.'
                              .format(host=host))
            raise e

        if host_address not in get_my_addresses():
            # Get real response from server
            method = self.response._request.command

            return requests.request(method=method,
                                    url=self.request_uri,
                                    timeout=1.5,
                                   **self.response._request.parameters)
        else:
            raise CircularReference(u'Error making request! Requested url resolves to this server!')

    def __modify(self,
                 response,
                 kind,
                 separator=u''):

        logging.debug(self._get_debug_separator(separator))

        modified = None
        request = self.request_uri
        headers = {}

        # Make Modifications to response
        try:
            # Get handlers for this request
            handlers = self.get_handlers_for_request(request=request,
                                                     kind=kind,
                                                     host=self.request_host)

            # Process handlers for this request
            for handler in handlers:

                try:
                    modifiers = self.get_modifiers_for_handler(handler[HandlerConstant.name])

                    if kind in [HandlerTypeConstant.uri, HandlerTypeConstant.canned]:
                        request = handler[HandlerConstant.instance].handle_request(request=request,
                                                                                   response=response,
                                                                                   client=self.client_address,
                                                                                   modifiers=modifiers)

                    elif kind == HandlerTypeConstant.header:
                        headers = handler[HandlerConstant.instance].handle_request(request=request,
                                                                                   response=response,
                                                                                   client=self.client_address,
                                                                                   modifiers=modifiers)

                    else:
                        response = handler[HandlerConstant.instance].handle_request(request=request,
                                                                                    response=response,
                                                                                    client=self.client_address,
                                                                                    modifiers=modifiers)

                except NoActiveModifiers as err:
                    pass
                    # logging.warning(self.prefix_message(u'No modifiers found!'))

            # Return the appropriate value
            if kind in (HandlerTypeConstant.uri, HandlerTypeConstant.canned):
                modified = request

            elif kind == HandlerTypeConstant.header:
                modified = headers

        except NoHandlersFound as err:
            pass
            # logging.debug(err)

        except Exception as err:
            logging.exception(err)

        # logging.debug(self._get_debug_separator(u'END {s}'.format(s=separator)))

        return modified

    def get_handlers_for_request(self,
                                 request,
                                 host,
                                 kind=None):
        handlers = []

        # Get the handlers for this request
        if kind in [HandlerTypeConstant.uri,
                    HandlerTypeConstant.canned,
                    HandlerTypeConstant.header]:

            try:
                handlers = self.get_handlers_for_kind(kind)

            except NoActiveModifiers:
                pass
                # logging.debug(u'No active modifiers found for {kind} handler.'.format(kind=kind))

        else:
            try:
                handlers = self.get_handlers_for_kind(HandlerTypeConstant.body)

            except NoActiveModifiers:
                pass

            try:
                handlers.extend(self.get_handlers_for_uri(uri=request))

            except NoActiveModifiers:
                pass

        # logging.debug(u'Handlers: {handlers}'.format(handlers=handlers))

        if len(handlers) == 0:
            raise NoHandlersFound(u'No handlers found for {uri} or {kind}!'.format(uri=request,
                                                                                   kind=kind))

        return handlers

    def get_handlers_for_uri(self,
                             uri=None):
        try:
            endpoint = Endpoints().get_endpoint_for_request(uri)

        except LookupError as err:
            raise NoHandlersFound(u'No handlers found for {uri}! Err: {e}'.format(uri=uri,
                                                                                  e=err))

        try:
            handlers = []
            for handler in self._handlers.values():
                if handler.get(HandlerConstant.api) == endpoint.api:
                    if handler[HandlerConstant.instance].can_you_handle(uri):
                        handlers.append(handler)

            return handlers

        except Exception as err:
            logging.exception(err)
            raise Exception(u'Unknown exception while getting handlers for {uri}'.format(uri=uri))

    def get_handlers_for_host(self,
                              host):
        try:
            # TODO: Are we going to configure this separately from endpoints?
            apis = Endpoints().get_endpoint_apis()
            apis = apis.get(host, [])
            logging.debug(apis)

            handlers = []
            for handler in self._handlers.values():
                if handler.get(HandlerConstant.api) in apis:
                    handlers.append(handler)

            return handlers

        except Exception as err:
            logging.exception(err)
            raise Exception(u'Unknown exception while getting handlers for {host}'
                            .format(host=host))

    def get_handlers_for_kind(self,
                              kind):
        handlers = []

        # logging.debug(u'Looking for {kind} handler.'.format(kind=kind))

        try:
            if kind in [h.name for h in self._scenarios.scenario_handlers]:
                handlers.append(self._handlers[kind])

            return handlers

        except Exception as err:
            logging.exception(err)
            raise Exception(u'Unknown exception while getting handlers for {kind}'.format(kind=kind))

    def get_modifiers_for_handler(self,
                                  handler_name):

        modifiers = [# m
                     copy.deepcopy(m)
                     for m in self._scenarios.scenario_modifiers
                     if m[ModifierConstant.handler] == handler_name]

        # For each modifier retreive the loaded module and add it to the modifier
        # TODO: There is probably a better way to integrate the modifier config & loaded module config!
        for i, mod in enumerate(modifiers):
            mod_key = u'{h}.{m}'.format(h=mod.handler,
                                        m=mod.modifier)
            setattr(modifiers[i], ModifierConstant.module, self._modifiers[mod_key][ModifierConstant.module])

        # logging.debug(u'Modifiers: {m}'.format(m=modifiers))

        if len(modifiers) == 0:
            raise NoActiveModifiers(u'No active modifiers found for {handler}!'.format(handler=handler_name))

        return modifiers

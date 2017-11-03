# encoding: utf-8

import logging_helper
from abc import abstractmethod

logging = logging_helper.setup_logging()

MATCHES = u'matches'
LIBRARY = u'library'


class BaseInterceptHandler(object):

    # Override I_CAN_HANDLE_THIS with a string
    # or I_CAN_HANDLE_THESE with list of strings
    # to match in the response urls. If the url
    # contains one of the strings
    # it will be matched and handled.

    # I_CAN_HANDLE_THIS = u''
    # I_CAN_HANDLE_THESE = []

    def __init__(self):

        # TODO: Is this init really necessary?
        try:
            self.I_CAN_HANDLE_THIS
            self.I_CAN_HANDLE_THESE = [self.I_CAN_HANDLE_THIS]
        except:
            try:
                self.I_CAN_HANDLE_THESE
            except:
                self.I_CAN_HANDLE_THESE = [u'']

    def can_you_handle(self,
                       request):
        return request is None or any((True
                                       for body in self.I_CAN_HANDLE_THESE
                                       if body in request))

    @staticmethod
    def _validate_modifier_type(modifier_type,
                                modifier):
        return modifier.handler == modifier_type or modifier.modifier.startswith(modifier_type)
        # TODO: is 2nd check necessary?

    @abstractmethod
    def handle_request(self,
                       request,
                       response,
                       client,
                       modifiers):

        """
        
        :param request:     Original request
        :param response:    Real response for modifying.  Can also be None
        :param client:      Requesting client details. tuple (host, port).  Can also be None
        :param modifiers:   Active modifiers for this handler
        :return:            Modified response
        """

        pass

# encoding: utf-8

import logging_helper
from ._base import BaseInterceptHandler
from pyhttpintercept.config.constants import HandlerTypeConstant

logging = logging_helper.setup_logging()


class InterceptHandler(BaseInterceptHandler):

    @staticmethod
    def get_canned_response(request,
                            modifier):

        response = modifier.module.modify(uri=request,
                                          parameters=modifier)

        logging.debug(u'Canned response: {r}'.format(r=response))

        return response

    def handle_request(self,
                       request,
                       response,
                       client,
                       modifiers):

        """
        Called by HTTP_Web Server to modify a request
        by returning a canned request/response.

        """

        # logging.debug(u'in {name}.modify_with_canned_request'.format(name=self.__class__.__name__))

        response = None
        if self.can_you_handle(request):  # Shouldn't need this check, but worth leaving in

            # apply all modifications:
            for modifier in modifiers:
                logging.debug(modifier)

                try:
                    if self._validate_modifier_type(modifier_type=HandlerTypeConstant.canned,
                                                    modifier=modifier):
                        response = self.get_canned_response(request=request,
                                                            modifier=modifier)

                except KeyError as err:
                    logging.exception(err)
                    logging.warning(u'{modifier} modifier does '
                                    u'not exist for {module}'.format(modifier=modifier.modifier,
                                                                     module=modifier.handler))

        return response

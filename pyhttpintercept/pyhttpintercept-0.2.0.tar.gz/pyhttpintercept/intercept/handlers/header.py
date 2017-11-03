# encoding: utf-8

import logging_helper
from ._base import BaseInterceptHandler
from pyhttpintercept.config.constants import HandlerTypeConstant

logging = logging_helper.setup_logging()


class InterceptHandler(BaseInterceptHandler):

    @staticmethod
    def modify_headers(request,
                       response,
                       modifier):

        response = modifier.module.modify(request=request,
                                          response=response,
                                          parameters=modifier)

        # logging.debug(u'Modified Headers: {r}'.format(r=response))

        return response

    def handle_request(self,
                       request,
                       response,
                       client,
                       modifiers):

        """
        Called by HTTP_Web Server to handle a message.
        There should be no need to modify or override this.

        Filters modifiers so that only the ones appropriate
        to the message are applied.

        If there are no modifiers or a modifier fails to load,
        just returns the original response.
        """

        # logging.debug(u'in {name}.handle_response_headers'.format(name=self.__class__.__name__))

        headers = {}

        if self.can_you_handle(request):  # Shouldn't need this check, but worth leaving in

            # apply all modifications:
            for modifier in modifiers:
                logging.debug(modifier)

                try:
                    if self._validate_modifier_type(modifier_type=HandlerTypeConstant.header,
                                                    modifier=modifier):
                        headers.update(
                            modifier.module.modify(request=request,
                                                   response=response,
                                                   parameters=modifier))

                except KeyError as err:
                    logging.exception(err)
                    logging.warning(u'{modifier} modifier does '
                                    u'not exist for {module}'.format(modifier=modifier.modifier,
                                                                     module=modifier.handler))

                finally:
                    logging.debug(u'Modified Headers: {r}'.format(r=headers))

        return headers

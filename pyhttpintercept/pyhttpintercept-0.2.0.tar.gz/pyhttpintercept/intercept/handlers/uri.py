# encoding: utf-8

import logging_helper
from ._base import BaseInterceptHandler
from pyhttpintercept.config.constants import HandlerTypeConstant

logging = logging_helper.setup_logging()


class InterceptHandler(BaseInterceptHandler):

    @staticmethod
    def modify_uri(request,
                   modifier):

        response = modifier.module.modify(uri=request,
                                          parameters=modifier)

        logging.debug(u'Modified URI response: {r}'.format(r=response))

        return response

    def handle_request(self,
                       request,
                       response,
                       client,
                       modifiers):

        """
        Called by HTTP_Web Server to modify a uri.
        There should be no need to modify or override this.

        Filters modifiers so that only the ones appropriate
        to the message are applied.

        If there are no modifiers or modifiers fails to load,
        just returns the original uri.

        """

        # logging.debug(u'in {name}.modify_request_uri'.format(name=self.__class__.__name__))

        if self.can_you_handle(request):  # Shouldn't need this check, but worth leaving in

            # apply all modifications:
            for modifier in modifiers:
                logging.debug(modifier)

                try:
                    if self._validate_modifier_type(modifier_type=HandlerTypeConstant.uri,
                                                    modifier=modifier):
                        request = self.modify_uri(request=request,
                                                  modifier=modifier)

                except KeyError as err:
                    logging.exception(err)
                    logging.warning(u'{modifier} modifier does '
                                    u'not exist for {module}'.format(modifier=modifier.modifier,
                                                                     module=modifier.handler))

        return request

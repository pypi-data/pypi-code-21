# encoding: utf-8

import logging_helper
from ._base import BaseInterceptHandler

logging = logging_helper.setup_logging()


class InterceptHandler(BaseInterceptHandler):

    @staticmethod
    def modify_body(request,
                    response,
                    modifier):

        try:
            response = modifier.module.modify(request=request,
                                              response=response,
                                              parameters=modifier)

            logging.debug(u'Modified response: {r}'.format(r=response))

        except Exception as e:
            logging.exception(e)
            logging.exception(u'Modifying failed:'
                              u'\n    handler   : {handler}'  # TODO: This can be replaced with unicode(modifier) 
                              u'\n    modifier  : {modifier}'
                              u'\n    filter    : {filter}'
                              u'\n    override  : {override}'
                              u'\n    parameters: {parameters}'.format(handler=modifier.handler,
                                                                       modifier=modifier.modifier,
                                                                       filter=modifier.filter,
                                                                       override=modifier.override,
                                                                       parameters=modifier.params,
                                                                       module=modifier.module))
        return response

    def handle_request(self,
                       request,
                       response,
                       client,
                       modifiers):

        """
        Called by HTTP_Web Server to modify the body of a response.
        There should be no need to modify or override this.

        Filters modifiers so that only the ones appropriate
        to the message are applied.

        If there are no modifiers or a modifier fails to load,
        just returns the original response.

        Does not modify if the response is 200.
        """

        # logging.debug(u'in {name}.handle_response'.format(name=self.__class__.__name__))

        if self.can_you_handle(request):  # Shouldn't need this check,  but worth leaving in

            # apply all modifications:
            for modifier in modifiers:
                logging.debug(modifier)

                try:
                    if response.status_code == 200:

                        response = self.modify_body(request=request,
                                                    response=response,
                                                    modifier=modifier)

                except KeyError as err:
                    logging.exception(err)
                    logging.warning(u'{modifier} modifier does '
                                    u'not exist for {module}'.format(modifier=modifier.modifier,
                                                                     module=modifier.handler))

        return response

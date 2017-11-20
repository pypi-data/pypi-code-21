import logging
import base64

from globus_sdk.authorizers.base import GlobusAuthorizer

logger = logging.getLogger(__name__)


class BasicAuthorizer(GlobusAuthorizer):
    """
    This Authorizer implements Basic Authentication.
    Given a "username" and "password", they are sent base64 encoded in the
    header.

    **Parameters**

        ``username`` (*string*)
          Username component for Basic Auth

        ``password`` (*string*)
          Password component for Basic Auth
    """
    def __init__(self, username, password):
        logger.info(("Setting up a BasicAuthorizer. It will use an "
                     "auth type of Basic and cannot handle 401s."))
        logger.info("BasicAuthorizer.username = {}".format(username))
        self.username = username
        self.password = password

        encoded = base64.b64encode(
            bytes("{0}:{1}".format(username, password).encode("utf-8")))
        self.header_val = "Basic %s" % encoded.decode('utf-8')

    def set_authorization_header(self, header_dict):
        """
        Sets the ``Authorization`` header to
        "Basic <base64 encoded username:password>"
        """
        logger.debug(("Setting Basic Authorization Header: "
                      '"Basic <{}:SECRET>"').format(self.username))
        header_dict['Authorization'] = self.header_val

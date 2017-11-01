import logging


from globus_sdk.response import GlobusResponse, GlobusHTTPResponse
from globus_sdk.transfer import TransferClient
from globus_sdk.transfer.data import TransferData, DeleteData
from globus_sdk.auth import (
    AuthClient, NativeAppAuthClient, ConfidentialAppAuthClient)

from globus_sdk.authorizers import (
    NullAuthorizer, BasicAuthorizer, AccessTokenAuthorizer,
    RefreshTokenAuthorizer, ClientCredentialsAuthorizer)

from globus_sdk.exc import GlobusError, GlobusAPIError, TransferAPIError
from globus_sdk.exc import (
    NetworkError, GlobusConnectionError, GlobusTimeoutError)

from globus_sdk.version import __version__

__all__ = ["GlobusResponse", "GlobusHTTPResponse",

           "TransferClient", "TransferData", "DeleteData",

           "AuthClient",
           "NativeAppAuthClient",
           "ConfidentialAppAuthClient",

           "NullAuthorizer", "BasicAuthorizer",
           "AccessTokenAuthorizer", "RefreshTokenAuthorizer",
           "ClientCredentialsAuthorizer",

           "GlobusError", "GlobusAPIError", "TransferAPIError",
           "NetworkError", "GlobusConnectionError", "GlobusTimeoutError",
           "GlobusOptionalDependencyError",

           "__version__"]


# configure logging for a library, per python best practices:
# https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
# NB: this won't work on py2.6 because `logging.NullHandler` wasn't added yet
logging.getLogger('globus_sdk').addHandler(logging.NullHandler())

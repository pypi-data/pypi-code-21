
# Get module version
from _metadata import __version__

# Import key items from module
from .server import (ThreadedHTTPWebServer,
                     HTTPWebServer)

from .request import (HTTPRequestHandler,
                      HTTPRequestHandlerWithProfiling)

from .intercept.handlers import (BaseInterceptHandler,
                                 BodyInterceptHandler)

# Set default logging handler to avoid "No handler found" warnings.
from logging import NullHandler, getLogger
getLogger(__name__).addHandler(NullHandler())

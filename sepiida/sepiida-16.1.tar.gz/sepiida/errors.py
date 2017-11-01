import json
import logging

from werkzeug.exceptions import HTTPException

LOGGER = logging.getLogger(__name__)

class SepiidaError(Exception):
    pass

class AppError(SepiidaError):
    pass

class RoutingError(SepiidaError):
    pass

class Specification():
    """
    This class is in charge of identifying the errors that an APIEndpoint may emit. They act as a sort of translation between
    internal error types and HTTP status codes with error title and description. If a status_code, error_code, title or details
    are provided then they will be used any time an exception is raised inside the request handler that matches the type of
    this specification.

    The `docs` get extracted from this class when producing RAML documentation on the errors an endpoint may emit
    """
    def __init__(self, exception_class, status_code=None, error_code=None, title=None, details=None, docs=None):
        self.details            = details
        self.docs               = docs
        self.error_code         = error_code
        self.exception_class    = exception_class
        self.status_code        = status_code
        self.title              = title

    def translate(self, exception):
        if not isinstance(exception, self.exception_class):
            raise TypeError("Cannot translate {}, it isn't an instance of {}".format(exception, self.exception_class))

        details     = self.details if self.details else getattr(exception, 'details', None)
        error_code  = self.error_code if self.error_code else getattr(exception, 'error_code', self.exception_class.__name__)
        status_code = self.status_code if self.status_code else getattr(exception, 'status_code', 400)
        title       = self.title if self.title else getattr(exception, 'title', str(exception))
        return Error(
            details     = details,
            error_code  = error_code,
            status_code = status_code,
            title       = title,
        )

    def __str__(self):
        return "Error Specification {} -> {} ({})".format(self.exception_class, self.status_code, self.error_code)

    def __repr__(self):
        return str(self)

class Error(SepiidaError):
    def __init__(self, error_code, title, details=None, status_code=400):
        super().__init__()
        self.details        = details
        self.error_code     = error_code
        self.status_code    = status_code
        self.title          = title

    def to_dict(self):
        result = {
            'code'  : self.error_code,
            'title' : self.title,
        }
        if self.details is not None:
            result['details'] = self.details
        return result

class APIException(HTTPException):
    def __init__(self, errors, status_code=None, headers=None):
        super().__init__()
        self.errors         = errors
        self.headers        = headers if headers is not None else {'Content-Type': 'application/json'}
        self._status_code   = status_code

    @property
    def code(self):
        return self._status_code if self._status_code is not None else self.errors[0].status_code

    @property
    def data(self):
        return {'errors': [e.to_dict() for e in sorted(self.errors, key=lambda x: x.error_code + x.title)]}

    def get_body(self, environ=None):
        return json.dumps(self.data)

    def get_headers(self, environ=None):
        return self.headers

class AuthenticationException(HTTPException):
    def __init__(self, status_code=403, error_code='unauthorized', title='You are not authorized'):
        super().__init__()
        self.code       = status_code
        self.error_code = error_code
        self.title      = title

    def get_body(self, environ=None):
        return json.dumps({
            'errors'    : [{
                'code'  : self.error_code,
                'title' : self.title,
            }]
        })

    def get_headers(self, environ=None):
        return {'WWW-Authenticate': 'Custom realm="Authentise"'}

def api_error(title="An error occurred", status_code=400, error_code='error'):
    # Translate from the outer names so that the inner names can shadow without
    # losing data and without having to use a different parameter name at each level
    defaults = {
        'error_code'    : error_code,
        'status_code'   : status_code,
        'title'         : title,
    }
    def __init__(self, title=None, status_code=None, error_code=None): # pylint: disable=unused-argument
        my_kwargs = defaults.copy()
        for prop in ['title', 'status_code', 'error_code']:
            val = locals()[prop]
            if val is not None:
                my_kwargs[prop] = val
        Error.__init__(self, **my_kwargs)
    name = 'generated-exception-class'
    return type(name, (Error,), {'__init__': __init__})


EmptyPayload        = api_error(status_code=400, error_code='empty-payload')
InvalidPayload      = api_error(status_code=400, error_code='invalid-payload')
ResourceNotFound    = api_error(status_code=404, error_code="resource-not-found")
Unauthorized        = api_error(status_code=403, error_code="Unauthorized")
UnableToSerialize   = api_error(status_code=400,
    error_code  = 'unable-to-serialize',
    title       = ("No serializers are able to respond in a format you would accept. "
                   "Check your Accept header and alter it to accept more types for this request")
)

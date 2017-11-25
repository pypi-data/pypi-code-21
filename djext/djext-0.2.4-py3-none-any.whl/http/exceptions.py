class HttpError(Exception):
    _error_class_map = {}
    status_code = None

    @classmethod
    def register_error_class(cls, status_code, error_class, override_existing=False):
        try:
            status_code = int(status_code)
        except:
            raise ValueError('Status code must be an integer')
        if status_code in cls._error_class_map and not override_existing:
            raise KeyError(f'Status code {status_code} is already registered')
        if not issubclass(error_class, cls):
            raise ValueError(f'Error class must be a subclass of HttpError')
        cls._error_class_map[status_code] = error_class

    @classmethod
    def with_status_code(cls, status_code, *args, **kwargs):
        if status_code in cls._error_class_map:
            return cls._error_class_map[status_code](*args, **kwargs)
        else:
            return cls(status_code, *args, **kwargs)

    def __init__(self, status=None, reason=None, *args, **kwargs):
        if status is not None:
            try:
                self.status_code = int(status)
            except (ValueError, TypeError):
                raise TypeError('HTTP status code must be an integer.')

        if not 100 <= self.status_code <= 599:
            raise ValueError('HTTP status code must be an integer from 100 to 599.')

        self.reason = reason
        super().__init__(*args, **kwargs)


class HttpErrorRedirectBase(HttpError):
    def __init__(self, redirect_to, *args, **kwargs):
        self.location = redirect_to
        super().__init__(*args, **kwargs)


class HttpErrorPermanentRedirect(HttpErrorRedirectBase):
    status_code = 301


class HttpErrorRedirect(HttpErrorRedirectBase):
    status_code = 302


class HttpErrorBadRequest(HttpError):
    status_code = 400


class HttpErrorUnauthorized(HttpError):
    status_code = 401


class HttpErrorForbidden(HttpError):
    status_code = 403


class HttpErrorNotFound(HttpError):
    status_code = 404


class HttpErrorNotAllowed(HttpError):
    status_code = 405


class HttpErrorGone(HttpError):
    status_code = 410


class HttpErrorInternalServerError(HttpError):
    status_code = 500


_status_code_map = (
    (301, HttpErrorPermanentRedirect),
    (302, HttpErrorRedirect),
    (400, HttpErrorBadRequest),
    (401, HttpErrorUnauthorized),
    (403, HttpErrorForbidden),
    (404, HttpErrorNotFound),
    (405, HttpErrorNotAllowed),
    (410, HttpErrorGone),
    (500, HttpErrorInternalServerError),
)
for status_code, error_class in _status_code_map:
    HttpError.register_error_class(status_code, error_class)

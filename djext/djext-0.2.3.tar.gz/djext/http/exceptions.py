class HttpError(Exception):
    status_code = None

    def __init__(self, status=None, reason=None, *args: object) -> None:
        if status is not None:
            try:
                self.status_code = int(status)
            except (ValueError, TypeError):
                raise TypeError('HTTP status code must be an integer.')

        if not 100 <= self.status_code <= 599:
            raise ValueError('HTTP status code must be an integer from 100 to 599.')

        self.reason = reason
        super().__init__(*args)


class HttpErrorRedirectBase(HttpError):
    def __init__(self, redirect_to, *args: object) -> None:
        self.location = redirect_to
        super().__init__(*args)


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

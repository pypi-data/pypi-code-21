"""
Exceptions module of the api
"""


class VerigatorError(Exception):
    """
    Base error class for all verigator related errors.
    """

    def __init__(self, code, message):
        super(VerigatorError, self).__init__(message)
        self.code = code
        self.message = message


class InvalidDataError(VerigatorError):
    """
    This error is raised when provided data is invalid
    """

    def __init__(self, code, message):
        super(InvalidDataError, self).__init__(code, message)


class NoSuchResourceError(VerigatorError):
    """
    This error is raised when the resource that yu were looking for does not exist
    """

    def __init__(self, code, message):
        super(NoSuchResourceError, self).__init__(code, message)


class ResourceAlreadyExistsError(VerigatorError):
    """
    This error is raised when you are creating resource that already exists
    """

    def __init__(self, code, message):
        super(ResourceAlreadyExistsError, self).__init__(code, message)


class ResourceForbiddenError(VerigatorError):
    """
    This error raises when you don't have permissions to access the resource
    """

    def __init__(self, code, message):
        super(ResourceForbiddenError, self).__init__(code, message)


class WrongCredentialsError(VerigatorError):
    """
    This error raises when you provided invalid credentials.
    Please see messente dashboard for correct username and password
    """
    def __init__(self, code, message):
        super(WrongCredentialsError, self).__init__(code, message)


class InternalError(VerigatorError):
    """
    This error means that there is a problem on the server side.
    """

    def __init__(self, code, message):
        super(InternalError, self).__init__(code, message)


class InvalidResponseError(VerigatorError):
    """
    This error usually raises when server returned non-json response
    """
    def __init__(self, code, message):
        super(InvalidResponseError, self).__init__(code, message)

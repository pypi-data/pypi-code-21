class BaseGuideError(Exception):
    def __init__(self, *args, **kwargs):
        super(BaseGuideError, self).__init__(*args, **kwargs)


class ValidationError(BaseGuideError):
    def __init__(self, message):
        super(ValidationError, self).__init__(message)


class HttpError(BaseGuideError):
    def __init__(self, message):
        super(HttpError, self).__init__(message)


class AuthError(BaseGuideError):
    def __init__(self, message):
        super(AuthError, self).__init__(message)


class ImpersonateError(BaseGuideError):
    def __init__(self, message):
        super(ImpersonateError, self).__init__(message)


class RequestEntityTooLargeError(BaseGuideError):
    def __init__(self, message):
        super(RequestEntityTooLargeError, self).__init__(message)


class ForbiddenError(BaseGuideError):
    def __init__(self, message):
        super(ForbiddenError, self).__init__(message)


class InvalidDataError(Exception):
    def __init__(self, message):
        super(InvalidDataError, self).__init__(message)


class GitLabAbortError(Exception):
    def __init__(self):
        super(GitLabAbortError, self).__init__("GitLab unknown error")


class BadRequestError(BaseGuideError):  # 400
    def __init__(self, message):
        super(BadRequestError, self).__init__(message)

class ResourceNotFoundError(BaseGuideError):    # 404
    def __init__(self, message):
        super(ResourceNotFoundError, self).__init__("Requested resource doesn't exist: {0}", message)

class MethodNotAllowedError(BaseGuideError):    # 405
    def __init__(self, message):
        super(MethodNotAllowedError, self).__init__("Method Not Allowed: {0}".format(message))

class ConflictError(BaseGuideError):    # 409
    def __init__(self):
        super(ConflictError, self).__init__("Resource version on the server is newer than on the client")


class ServerError(BaseGuideError):  # 500
    def __init__(self):
        super(ServerError, self).__init__("ServerError Error")


class UnknownError(BaseGuideError):
    def __init__(self):
        super(UnknownError, self).__init__("Unknown error from elastic search")


class GitUnknownError(BaseGuideError):
    def __init__(self):
        super(UnknownError, self).__init__("Unknown error from GitLab")

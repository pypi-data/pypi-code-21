
# Guide specific exceptions
# JP: TODO think about whether exceptions should all be logged


class BaseGuideError(Exception):
    """
    Base exception class for Guide .
    """
    def __init__(self, *args, **kwargs):
        super(BaseGuideError, self).__init__(*args, **kwargs)


class CommitError(BaseGuideError):
    def __init__(self, message):
        super(CommitError, self).__init__(message)


class ValidationError(BaseGuideError):
    def __init__(self, message):
        super(ValidationError, self).__init__(message)


class JSONDecodeError(BaseGuideError):
    """
    Unable to decode received JSON.
    """
    def __init__(self, response):
        self.response = response
        super(JSONDecodeError, self).__init__(
            'Unable to decode received JSON, you can inspect exception\'s '
            '"response" attribute to find out what the response was'
        )

# ElasticSearch error returns
# JP: I couldn't find very good documentation for these TODO maybe need to look harder for docs and revise these
# JP TODO also think about security implications of error returns and whether these get back to the client


class BadRequestError(BaseGuideError):  # 400
    def __init__(self, message):
        super(BadRequestError, self).__init__(message)


class ResourceNotFoundError(BaseGuideError):    # 404
    def __init__(self):
        super(ResourceNotFoundError, self).__init__("Requested resource doesn't exist")


class ConflictError(BaseGuideError):    # 409
    def __init__(self):
        super(ConflictError, self).__init__("Resource version on the server is newer than on the client")


class PreconditionError(BaseGuideError):    # 412
    def __init__(self):
        super(PreconditionError, self).__init__("Precondition Error")


class ServerError(BaseGuideError):  # 500
    def __init__(self):
        super(ServerError, self).__init__("ServerError Error")

class ElasticsearchError(BaseGuideError):  # 500
    def __init__(self, message):
        super(ElasticsearchError, self).__init__("Elasticsearch Error {0}".format(message))



class ServiceUnreachableError(BaseGuideError):  # 503
    def __init__(self):
        super(ServiceUnreachableError, self).__init__("ServerError Error")


class ResultParseError(BaseGuideError):
    def __init__(self, message):
        super(BadRequestError, self).__init__("ElasticSearch return not in expected format {}".format(message))


class UnknownError(BaseGuideError):
    def __init__(self, message):
        super(UnknownError, self).__init__("Unknown error from elastic search{0}".format(message))

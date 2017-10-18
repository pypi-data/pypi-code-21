from openapi_core import request_parameters_factory, request_body_factory
from openapi_core.exceptions import InvalidServerError


class RequestValidator(object):

    def __init__(self, spec, request):
        self.spec = spec
        self.request = request
        self.is_validated = False

    def validate(self):
        self.is_validated = True
        for error in self.iter_errors():
            raise error

    def iter_errors(self):
        yield from RequestServerValidator(self.spec).validate(self.request)

        operation_pattern = self.request.full_url_pattern.replace(
            server.default_url, '')

    @property
    def body(self):
        if not self.is_validated:
            self.validate()

        return request_body_factory.create(self.request, self.spec)

    @property
    def parameters(self):
        if not self.is_validated:
            self.validate()

        return request_parameters_factory.create(self.request, self.spec)


class RequestServerValidator(object):

    def __init__(self, spec):
        self.spec = spec

    def iter_errors(self, request):
        for server in self.spec.servers:
            if server.default_url in request.full_url_pattern:
                return server

        raise InvalidServerError(
            "Invalid request server {0}".format(
                request.full_url_pattern)
        )

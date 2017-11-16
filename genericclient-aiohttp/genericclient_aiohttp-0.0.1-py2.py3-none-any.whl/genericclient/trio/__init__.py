from functools import partial

import asks
import trio

from . import Endpoint, GenericClient, exceptions

asks.init('trio')


class TrioEndpoint(Endpoint):
    def http_request(self, method, *args, **kwargs):
        kwargs['auth'] = self.api.auth
        kwargs['auth_off_domain'] = True
        kwargs['headers'] = {
            'host': self.api.host,
            'content-type': 'application/json',
        }
        request_method = getattr(self.api.session, method)
        fn = partial(request_method, *args, **kwargs)
        return trio.run(fn)

    def request(self, method, *args, **kwargs):
        response = self.http_request(method, *args, **kwargs)

        if response.status_code == 403:
            raise exceptions.NotAuthenticatedError(response, "Cannot authenticate user `{}` on the API".format(self.api.session.auth[0]))
        elif response.status_code == 400:
            raise exceptions.BadRequestError(
                response,
                "Bad Request 400: {}".format(response.text)
            )
        return response


class TrioGenericClient(GenericClient):
    endpoint_class = TrioEndpoint
    session_class = asks.Session

    def set_auth(self, auth):
        self.auth = auth

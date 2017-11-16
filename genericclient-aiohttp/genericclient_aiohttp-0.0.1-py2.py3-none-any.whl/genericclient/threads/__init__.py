from requests_threads import AsyncSession
from twisted.internet.defer import inlineCallbacks

from . import Endpoint, GenericClient, Resource, exceptions


@inlineCallbacks
def hydrate_json(response):
    try:
        result = yield response.json()
        return result
    except ValueError:
        raise ValueError(
            "Response from server is not valid JSON. Received {}: {}".format(
                response.status_code,
                response.text,
            ),
        )


class TXEndpoint(Endpoint):
    @inlineCallbacks
    def request(self, method, *args, **kwargs):
        response = yield getattr(self.api.session, method)(*args, **kwargs)

        if response.status_code == 403:
            raise exceptions.NotAuthenticatedError(response, "Cannot authenticate user `{}` on the API".format(self.api.session.auth[0]))
        elif response.status_code == 400:
            raise exceptions.BadRequestError(
                response,
                "Bad Request 400: {}".format(response.text)
            )
        return response

    @inlineCallbacks
    def filter(self, **kwargs):
        response = yield self.request('get', self.url, params=kwargs)
        results = yield hydrate_json(response)
        return [Resource(self, **result) for result in results]

    @inlineCallbacks
    def all(self):
        results = yield self.filter()
        return results

    @inlineCallbacks
    def get(self, **kwargs):
        if 'id' in kwargs:
            url = self._urljoin(kwargs['id'])
            response = yield self.request('get', url)
        elif 'uuid' in kwargs:
            url = self._urljoin(kwargs['uuid'])
            response = yield self.request('get', url)
        elif 'pk' in kwargs:
            url = self._urljoin(kwargs['pk'])
            response = yield self.request('get', url)
        elif 'slug' in kwargs:
            url = self._urljoin(kwargs['slug'])
            response = yield self.request('get', url)
        elif 'username' in kwargs:
            url = self._urljoin(kwargs['username'])
            response = yield self.request('get', url)
        else:
            url = self.url
            response = yield self.request('get', url, params=kwargs)

        if response.status_code == 404:
            raise exceptions.ResourceNotFound("No `{}` found for {}".format(self.name, kwargs))

        result = yield hydrate_json(response)

        if isinstance(result, list):
            if len(result) == 0:
                raise exceptions.ResourceNotFound("No `{}` found for {}".format(self.name, kwargs))
            if len(result) > 1:
                raise exceptions.MultipleResourcesFound("Found {} `{}` for {}".format(len(result), self.name, kwargs))

            return Resource(self, **result[0])

        return Resource(self, **result)

    @inlineCallbacks
    def create(self, payload):
        response = yield self.request('post', self.url, json=payload)
        if response.status_code != 201:
            raise exceptions.HTTPError(response)

        result = yield hydrate_json(response)
        return Resource(self, **result)

    @inlineCallbacks
    def get_or_create(self, **kwargs):
        defaults = kwargs.pop('defaults', {})
        try:
            resource = yield self.get(**kwargs)
            return resource
        except exceptions.ResourceNotFound:
            params = {k: v for k, v in kwargs.items()}
            params.update(defaults)
            resource = yield self.create(params)
            return resource

    @inlineCallbacks
    def create_or_update(self, payload):
        if 'id' in payload or 'uuid' in payload:
            return Resource(self, **payload).save()

        result = yield self.create(payload)
        return result

    @inlineCallbacks
    def delete(self, pk):
        url = self._urljoin(pk)

        response = yield self.request('delete', url)

        if response.status_code != 204:
            raise exceptions.HTTPError(response)

        return None


class TXGenericClient(GenericClient):
    endpoint_class = TXEndpoint
    session_class = lambda x: AsyncSession(n=100)

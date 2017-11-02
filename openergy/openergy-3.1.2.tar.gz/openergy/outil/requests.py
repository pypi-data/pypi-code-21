import time
import uuid

import requests
from requests import exceptions

from .json import loads as json_loads
from .exceptions import ClientResponseError


class RequestsClient:
    """
    Raises
    ------
    ClientResponseError
    """
    _WAIT_FREQ = 0.5

    def __init__(self, host, port, credentials=None):
        """
        credentials: login, password
        """
        if "http" not in host:
            host = "http://%s" % host

        self.base_url = "%s:%s" % (host, port)
        self.session = requests.Session()
        if credentials is not None:
            self.session.auth = credentials

    @staticmethod
    def check_rep(rep):
        if (rep.status_code // 100) != 2:
            raise ClientResponseError(rep.text, rep.status_code)

    @classmethod
    def rep_to_json(cls, rep):
        cls.check_rep(rep)
        # we use our json loads for date parsing
        return json_loads(rep.text)

    def wait_for_on(self, timeout=10, freq=1):
        start = time.time()
        if timeout <= 0:
            raise ValueError
        while True:
            if (time.time() - start) > timeout:
                raise TimeoutError
            try:
                self._check_is_on_request()
                break
            except (exceptions.ConnectionError, TimeoutError):
                pass
            time.sleep(freq)

    def _check_is_on_request(self):
        raise NotImplementedError


class RESTClient(RequestsClient):
    def __init__(self, host, port, credentials=None, root_endpoint="", is_on_resource="/", verify_ssl=True):
        """
        is_on_resource: put None if you don't want to use it
        """
        super().__init__(host, port, credentials=credentials)
        self.base_endpoint_url = self.base_url + "/" + root_endpoint.strip("/")
        self._is_on_request = is_on_resource
        self.verify_ssl = verify_ssl  # todo: understand why it doesn't work

    def list(self, resource, params=None):
        resource = resource.strip("/")
        rep = self.session.get("%s/%s/" % (self.base_endpoint_url, resource), params=params, verify=self.verify_ssl)
        return self.rep_to_json(rep)

    def list_iter_all(self, resource, params=None):
        start = 0
        if params is None:
            params = {}
        while True:
            params["start"] = start
            current = self.list(resource, params=params)
            data = current["data"]
            if len(data) == 0:  # todo: should not need to perform last request
                break
            start += len(data)
            for element in data:
                yield element

    def retrieve(self, resource, resource_id):
        resource = resource.strip("/")
        rep = self.session.get("%s/%s/%s/" % (self.base_endpoint_url, resource, resource_id), verify=self.verify_ssl)
        return self.rep_to_json(rep)

    def create(self, resource, data):
        resource = resource.strip("/")
        rep = self.session.post("%s/%s/" % (self.base_endpoint_url, resource), json=data, verify=self.verify_ssl)
        return self.rep_to_json(rep)

    def partial_update(self, resource, resource_id, data):
        resource = resource.strip("/")
        rep = self.session.patch("%s/%s/%s/" % (self.base_endpoint_url, resource, resource_id), json=data,
                                 verify=self.verify_ssl)
        return self.rep_to_json(rep)

    def update(self, resource, resource_id, data):
        resource = resource.strip("/")
        rep = self.session.put("%s/%s/%s/" % (self.base_endpoint_url, resource, resource_id), json=data,
                               verify=self.verify_ssl)
        return self.rep_to_json(rep)

    def detail_route(self, resource, resource_id, http_method, method_name, params=None, data=None, return_json=True,
                     send_json=True):
        resource = resource.strip("/")
        rep = getattr(self.session, http_method.lower())(
            "%s/%s/%s/%s/" % (self.base_endpoint_url, resource, resource_id, method_name), params=params,
            json=data if send_json else None,
            data=None if send_json else data,
            verify=self.verify_ssl
        )
        if rep.status_code == 204:
            return

        if return_json:
            return self.rep_to_json(rep)
        self.check_rep(rep)
        return rep.content

    def list_route(self, resource, http_method, method_name, params=None, data=None, return_json=True, send_json=True):
        resource = resource.strip("/")
        rep = getattr(self.session, http_method.lower())(
            "%s/%s/%s/" % (self.base_endpoint_url, resource, method_name), params=params,
            json=data if send_json else None,
            data=None if send_json else data,
            verify=self.verify_ssl
        )
        if rep.status_code == 204:
            return

        if return_json:
            return self.rep_to_json(rep)
        self.check_rep(rep)
        return rep.content

    def destroy(self, resource, resource_id, params=None):
        resource = resource.strip("/")
        rep = self.session.delete("%s/%s/%s/" % (self.base_endpoint_url, resource, resource_id), params=params,
                                  verify=self.verify_ssl)
        if rep.status_code == 204:
            return
        return self.rep_to_json(rep)

    def _check_is_on_request(self):
        if self._is_on_request is None:
            raise NotImplementedError
        rep = self.session.get(self.base_endpoint_url + "/" + self._is_on_request.strip("/") + "/",
                               verify=self.verify_ssl)
        if rep.status_code == 503:
            raise TimeoutError


class RESTClientMock:
    custom_pks = None

    def __init__(self, host, port, credentials=None, root_endpoint="", is_on_resource="/"):
        """
        is_on_resource: put None if you don't want to use it
        """
        self._resources = {}  # {resource_name: {resource_pk: ...
        self.custom_pks = {} if self.custom_pks is None else self.custom_pks

    def _check_exists(self, resource):
        if resource not in self._resources:
            self._resources[resource] = {}

    def _get_pk(self, resource):
        return self.custom_pks[resource] if (resource in self.custom_pks) else "id"

    def reset(self):
        self._resources = {}

    def list(self, resource, params=None):
        resource = resource.strip("/")
        self._check_exists(resource)
        return list(self._resources[resource].values())

    def retrieve(self, resource, resource_pk):
        resource = resource.strip("/")
        self._check_exists(resource)
        if resource_pk not in self._resources[resource]:
            raise ClientResponseError(code=404)
        return self._resources[resource][resource_pk]

    def create(self, resource, data):
        resource = resource.strip("/")
        self._check_exists(resource)

        pk_key = self._get_pk(resource)
        if pk_key in data:
            resource_pk = data[pk_key]
        else:
            resource_pk = uuid.uuid4()
            data[pk_key] = resource_pk
        self._resources[resource][resource_pk] = data
        return data

    def partial_update(self, resource, resource_pk, data):
        resource = resource.strip("/")
        self._check_exists(resource)
        stored_resource = self.retrieve(resource, resource_pk)
        for k, v in data.items():
            stored_resource[k] = v
        return resource

    def detail_route(self, resource, resource_pk, http_method, method_name, params=None, data=None, return_json=True):
        resource = resource.strip("/")
        return {}

    def destroy(self, resource, resource_pk):
        resource = resource.strip("/")
        # check exists
        self.retrieve(resource, resource_pk)
        # delete
        del self._resources[resource][resource_pk]

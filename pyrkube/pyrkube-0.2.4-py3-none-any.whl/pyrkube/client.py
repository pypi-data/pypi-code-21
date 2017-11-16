"""
pyrkube.client
~~~~~~~~~~~~~~

API Client wrappers, etc for pyrkube.

:copyright: (c) 2017 by Joe Black.
:license: Apache2.
"""

import os
import collections

import pykube

from . import config, objects
from .adict import adict
from .exceptions import KubeConfigNotFound


SERVICE_ACCOUNT_PATH = '/var/run/secrets/kubernetes.io/serviceaccount'

WatchEvent = collections.namedtuple('WatchEvent', 'type object')


class KubeAPIClient:
    """A general-case client for interacting with kubernetes.

    Wraps the pykube library in a manner that is more similar to frequently
    used kubectl commands.
    """

    def __init__(self, env='dev', namespace='default', domain='cluster.local'):
        self.env = env
        self.namespace = namespace
        self.domain = domain
        self.api = self._get_api()

    @property
    def context(self):
        """Return the current kube context."""
        return self.api.config.contexts[self.api.config.current_context]

    @property
    def cluster(self):
        """Return the current kube cluster."""
        return self.context['cluster']

    @property
    def user(self):
        """Return the current kube user."""
        return self.context['user']

    @property
    def server(self):
        """Return the current kube server."""
        return self.api.config.cluster['server']

    def __repr__(self):
        return '%s(cluster: %s, user: %s, server: %s)' % (
            type(self).__name__, self.cluster, self.user, self.server
        )

    def _get_api(self):
        try:
            return pykube.http.HTTPClient(
                pykube.KubeConfig.from_service_account())
        except FileNotFoundError:
            kube_config = os.getenv('KUBECONFIG_PATH', '~/.kube/config')
            try:
                return pykube.http.HTTPClient(
                    pykube.KubeConfig.from_file(kube_config))
            except (FileNotFoundError, pykube.PyKubeError):
                raise KubeConfigNotFound('Could detect kube-config')

    @staticmethod
    def _get_resource_name(name):
        keys = list(objects.__dict__.keys())
        for key in keys:
            if key.lower() == name.lower():
                return key

    def _get_resources(self, name):
        # if name == 'node':
            # import pdb; pdb.set_trace()
        name = self._get_resource_name(name)
        return adict(
            pykube=getattr(pykube.objects, name),
            pyrkube=getattr(objects, name)
        )

    def get(self, resource, name=None, selector=None, namespace=False,
            watch=False, since=None):
        """Return an api object.

        Attributes:
          resource: (str) the pyrkube resource type to query
          name: (str) the metadata.name of the object to return
          selector: (dict) the label selector to query with
          namespace: (str) the namespace from which to query
          watch: (bool) return a watch query instead of just resource(s)
          since: (string) a resource version to pass to the watch query

        Returns:
          Either a Resource Object, list of Resource Objects, or if a watch
          query, a generator of Watch EVents.
        """
        if namespace is False:
            namespace = self.namespace

        resources = self._get_resources(resource)

        if not issubclass(resources.pykube, pykube.objects.APIObject):
            raise pykube.PyKubeError(
                'No pykube object of type: %s', resources.pykube
            )

        req = pykube.query.Query(
            self.api, resources.pykube, namespace=namespace
        )

        if selector:
            req = req.filter(selector=selector)
            if watch:
                req = req.watch(since)
        if name:
            req = req.get_or_none(name=name)
        if req:
            return self._wrap_resource(req, resources.pyrkube, namespace)

    def _wrap_resource(self, request, resource, namespace):
        api = self.clone(namespace)
        if isinstance(request, pykube.query.WatchQuery):
            return self._return_watch(api, request, resource)
        elif isinstance(request, pykube.query.Query):
            return [resource(api, obj) for obj in request.all()]
        elif isinstance(request, pykube.objects.APIObject):
            return resource(api, request)

    @staticmethod
    def _return_watch(api, request, resource):
        for evt in request:
            yield WatchEvent(evt.type, resource(api, evt.object))

    def clone(self, namespace=None):
        """Clone the api, optionally with a different namespace."""
        namespace = namespace or self.namespace
        return type(self)(self.env, namespace)


class KubeInterfaceBase:
    """Base Template for Kube Interface."""

    def __init__(self, environment=None, namespace=None, domain=None):
        self.environment = environment or config.ENVIRONMENT
        self.domain = domain or config.DOMAIN
        self.namespace = namespace or self._get_namespace()
        self.api = KubeAPIClient(self.environment, self.namespace)

    @staticmethod
    def _get_namespace():
        try:
            with open(SERVICE_ACCOUNT_PATH + '/namespace') as fd:
                return fd.read().strip()
        except FileNotFoundError:
            return 'default'

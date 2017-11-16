"""
pyrkube.objects
~~~~~~~~~~~~~~

API Resource objects for pyrkube.

:copyright: (c) 2017 by Joe Black.
:license: Apache2.
"""

import copy
import base64
import logging
import time
import abc

from . import util, hosts
from .adict import adict


class GenericBase(adict, metaclass=abc.ABCMeta):
    """Generic object base class."""
    def __init__(self, obj, *args, **kwargs):
        adict.__init__(self, obj, *args, **kwargs)


class ResourceBase(adict, metaclass=abc.ABCMeta):
    """Base class for pyrkube API resources."""
    def __init__(self, api, obj, *args, **kwargs):
        if not hasattr(self, 'kind'):
            raise NotImplementedError('%s must have kind attr', type(self))
        wrapper = obj
        obj = copy.deepcopy(wrapper.obj)
        obj['apiVersion'] = obj.get('apiVersion', wrapper.version)

        adict.__init__(self, obj, *args, **kwargs)
        self._wrapper = wrapper
        self._api = api
        self._init_defaults()
        self._deserialize_annotations()

    def _init_defaults(self):
        for key in ('labels', 'annotations'):
            if not self.metadata.get(key):
                self.metadata[key] = adict()

    def _deserialize_annotations(self):
        self.metadata.annotations = adict(
            {key: util.deserialize(val)
             for key, val in self.metadata.annotations.items()}
        )

    @property
    def name(self):
        """Return kubernetes metadata.name value."""
        return self.metadata.get('name')

    def __lt__(self, other):
        return self.name < other.name

    def reload(self):
        """Reload the object's data from the kubernetes API."""
        self = self._api.get(self.kind, self.name)


class Node(ResourceBase):
    """A Kubernetes Node Resource."""
    kind = 'Node'

    @property
    def ip(self):
        addrs = self['status']['addresses']
        return [a.address for a in addrs if a.type == 'InternalIP'][0]

    @property
    def hostname(self):
        addrs = self['status']['addresses']
        return [a.address for a in addrs if a.type == 'Hostname'][0]


class Pod(ResourceBase):
    """A Kubernetes Pod Resource."""
    kind = 'Pod'

    def __init__(self, api, obj):
        ResourceBase.__init__(self, api, obj)
        self._init_containers()

    def _init_containers(self):
        self.spec.containers = adict(
            (c.name, Container(self, c)) for c in self.spec.containers)

    @util.cached_property(ttl=30)
    def owner(self):
        """Returns the API object which owns this pod."""
        reference = self.metadata.annotations.get(
            'kubernetes.io/created-by', {}).get('reference')
        if reference:
            return self._api.get(reference.kind, reference.name)

    @property
    def ready(self):
        """Return true if this pod is in a ready state."""
        return (
            all([c.status for c in self.status.conditions]) and
            all([s.ready for s in self.status.containerStatuses]) and
            self.status.phase == 'Running'
        )


class Container(GenericBase):
    """A container within a pod or pod template."""
    def __init__(self, parent, obj):
        GenericBase.__init__(self, obj)
        self._parent = parent
        self._init_environment()

    def _init_environment(self):
        if hasattr(self, 'env'):
            self.env = ContainerEnv(self, {env.name: env for env in self.env})


class ContainerEnv(GenericBase):
    """The environment of a container in a pod or pod template.

    The environment is also resolved for all externally referenced values.
    """

    def __init__(self, container, obj):
        GenericBase.__init__(self, obj)
        self._container = container
        self._api = container._parent._api
        self._init_environment()

    def _init_environment(self):
        for key, val in self.items():
            setattr(self, key, self._lookup(val))

    def _lookup(self, env):
        if env.get('value'):
            return env.value
        elif env.get('valueFrom'):
            if env.valueFrom.get('secretKeyRef'):
                ref = env.valueFrom.secretKeyRef
                return self._api.get('secret', ref.name).get(ref.key)
            elif env.valueFrom.get('configMapKeyRef'):
                ref = env.valueFrom.configMapKeyRef
                return self._api.get('configmap', ref.name).get(ref.key)


class DataContainerBase(ResourceBase):
    """Base class for data container objects such as Secret or ConfigMap."""
    _encoded = None

    def __init__(self, api, obj):
        ResourceBase.__init__(self, api, obj)
        if self._encoded:
            self._decode_data()

    def _decode_data(self):
        for key, value in self.data.items():
            self.data[key] = base64.b64decode(value).decode()

    def get(self, key, default=None):
        """Get value in obj.data."""
        return self.data.get(key, default)


class ConfigMap(DataContainerBase):
    """A kubernetes ConfigMap."""
    kind = 'ConfigMap'
    _encoded = False


class Secret(DataContainerBase):
    """A kubernetes Secret."""
    kind = 'Secret'
    _encoded = True


class ReplicatedBase(ResourceBase):
    """Base Class for a replicated API object type such as Deployment."""
    def __init__(self, api, obj):
        ResourceBase.__init__(self, api, obj)
        self._init_containers()

    def _init_containers(self):
        self.spec.template.spec.containers = adict(
            (cont.name, Container(self, cont))
            for cont in self.spec.template.spec.containers
        )

    @util.cached_property(ttl=10)
    def pods(self):
        """Return the pods targeted by this replicated object template."""
        if self.spec.selector.get('matchLabels'):
            selector = self.spec.selector.get('matchLabels')
            return self._api.get('pod', selector=selector)


class ReplicaSet(ReplicatedBase):
    """A kubernetes ReplicaSet."""
    kind = 'ReplicaSet'

    @property
    def ready(self):
        """Return True if ready."""
        return (
            self.status.observedGeneration >= self.metadata.generation and
            self.status.readyReplicas == self.metadata.annotations.get(
                'deployment.kubernetes.io/desired-replicas'
            ) and
            all([pod.ready for pod in self.pods])
        )


class Deployment(ReplicatedBase):
    """A kubernetes Deployment"""
    kind = 'Deployment'

    @property
    def ready(self):
        """Return True if ready."""
        return (
            self.status.observedGeneration >= self.metadata.generation and
            self.status.updatedReplicas == self.spec.replicas and
            all([pod.ready for pod in self.pods])
        )


class DaemonSet(ReplicatedBase):
    """A kubernetes DaemonSet."""
    kind = 'DaemonSet'


class StatefulSet(ReplicatedBase):
    """A kubernetes StatefulSet."""
    kind = 'StatefulSet'

    @property
    def ready(self):
        """Return True if ready."""
        return (
            self.spec.replicas == self.status.replicas and
            all([pod.ready for pod in self.pods])
        )


class EndpointAddress(GenericBase):
    """A kubernetes Endpoint Address"""
    def __init__(self, endpoint, obj):
        GenericBase.__init__(self, obj)
        self._endpoint = endpoint

    @util.cached_property(ttl=10)
    def target(self):
        """Return the API object targeted by this Endpoint Address."""
        return self._endpoint._api.get(
            self.targetRef.kind, self.targetRef.name
        )


class Endpoint(ResourceBase):
    """A kubernetes Endpoint."""
    kind = 'Endpoints'

    def __init__(self, api, obj):
        ResourceBase.__init__(self, api, obj)
        self.subsets = [
            [EndpointAddress(self, addr) for addr in sub.addresses]
            for sub in self.subsets
        ]

    def _address_attribute(self, key):
        return sorted([getattr(addr, key) for addr in self.addresses])

    @property
    def addresses(self):
        """Return the addresses in this endpoint."""
        if len(self.subsets):
            return self.subsets[0]
        else:
            return self.subsets

    @property
    def ready(self):
        """Return True if all pods targeted by this endpoint are ready."""
        return all([pod.ready for pod in self.pods])

    @property
    def pods(self):
        """Return a list of pod objects targeted by this endpoint."""
        return self._address_attribute('target')

    @property
    def nodes(self):
        """Return a list of nodes targeted by this endpoint."""
        return self._address_attribute('nodeName')

    @property
    def ips(self):
        """Return a list of IPs targeted by this endpoint."""
        return self._address_attribute('ip')

    @property
    def hosts(self):
        """Return a list of hosts targeted by this endpoint."""
        return [host.hostname for host in self.hostnames]

    @property
    def hostnames(self):
        """Return a list of hostname objects targeted by this endpoint."""
        return [hosts.get_hostname(pod) for pod in self.pods]


class Service(ResourceBase):
    """A kubernetes Service."""
    kind = 'Service'

    @property
    def endpoint(self):
        """Return the endpoint object corresponding to this service."""
        return self._api.get('endpoint', self.name)


class KubeApp:
    """Abstraction for a kubernetes app.

    Designed to retrieve an application's readiness state.

    Attributes:
      api: (pyrkube.KubeAPIClient) the api object to use
      name: (str) the name of the deployment or statefulset
      sleep: (int) number of seconds to wait between polling state
    """

    def __init__(self, api, name, sleep=5):
        if not name:
            raise ValueError('name attribute must not be empty')
        self.api = api
        self.name = name
        self.sleep = sleep

    def __repr__(self):
        return '%s(%s %s %s)' % (
            type(self).__name__,
            self.kind,
            self.name,
            ', '.join(('%s=%r' % (a, getattr(self, a))
                       for a in ('loaded', 'ready')))
        )

    @util.cached_property(ttl=600)
    def kind(self):
        """Return the kubernetes api object kind."""
        return (
            self.api.get('deployment', self.name) or
            self.api.get('statefulset', self.name) or {}
        ).get('kind')

    @util.cached_property(ttl=30)
    def resource(self):
        """Return the API resource representing the app."""
        if self.kind:
            return self.api.get(self.kind, self.name)

    @property
    def loaded(self):
        """API Object exists in kubernetes."""
        return bool(self.resource)

    @property
    def ready(self):
        """API Object is in ready state."""
        return bool(self.resource) and self.resource.ready

    def poll(self):
        """Continually poll the state of the application."""
        while True:
            print(self)
            time.sleep(self.sleep)

    def wait(self):
        """Blocking wait until application is ready."""
        while not self.ready:
            time.sleep(self.sleep)

    def __bool__(self):
        return self.ready


class KubeApps(util.WrappedMapMixin):
    """Abstracted container for holding KubeApps.

    Attributes:
      api: (pyrkube.KubeAPIClient) the api object to use
      names: (list,tuple) names of deployment/statefulsets
      logger: (str) the name of a logger object to use.  Set to None for no
              logging
      sleep: (int) number of seconds to wait between polling state
    """
    def __init__(self, api, names, logger='kubeapp', sleep=5):
        if not isinstance(names, (list, tuple)):
            raise TypeError('names provided is not a list or tuple.')
        self.api = api
        self.names = names
        if logger:
            self.logging = True
            self.logger = logging.getLogger(logger)
        else:
            self.logging = False
        self.sleep = sleep
        self._init_apps()

    def _get_app(self, name):
        return KubeApp(self.api, name, self.wait)

    def _init_apps(self):
        self.apps = {a.name: a for a
                     in [self._get_app(n) for n in self.names]}
        self._wrapped = self.apps

    def __repr__(self):
        return '%s(apps: %s)' % (
            type(self).__name__,
            ', '.join(['%s' % app for app in self])
        )

    def __iter__(self):
        return iter(self.values())

    def log(self, *args):
        """If logging is enabled, log the following *args"""
        if self.logging:
            self.logger.info(*args)

    @property
    def status(self):
        """Return a dictionary of application names => ready states."""
        return {app.name: app.ready for app in self}

    @property
    def ready(self):
        """Return True if all apps are ready."""
        return all([app.ready for app in self])

    def poll(self):
        """Continually poll the state of the application."""
        while True:
            print(', '.join(self))
            time.sleep(self.sleep)

    def wait(self):
        """Blocking wait until all apps are ready.

        If logging enabled, detailed logs are output to the logger.
        """
        def log_status():
            """Log's the current status of the wait cycle."""
            msg = []
            if ready:
                msg.append('%d apps ready.' % ready)
            if apps:
                msg.append('waiting for %d apps: %s' % (
                    len(apps), ', '.join([app.name for app in apps])
                ))
            if msg:
                self.log(' '.join(msg))

        self.log('Loaded %d apps: %s', len(self.names), ', '.join(self.names))
        apps = list(self)
        ready = 0
        while apps:
            for app in apps[:]:
                if app.ready:
                    self.log('app: %s ready', app.name)
                    apps.remove(app)
                    ready += 1

            log_status()
            if apps:
                time.sleep(self.sleep)
            else:
                self.log('Finished')

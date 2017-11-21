import logging

import pyrkube
from pyrkube.objects import (
    Pod,
    ConfigMap,
    Secret,
    ReplicaSet,
    Deployment,
    StatefulSet,
    Endpoint,
    Service,
    KubeApp,
    KubeApps,
    Container,
    ContainerEnv,
    EndpointAddress,
    ResourceBase,
)
from pyrkube.adict import adict
from pyrkube.hosts import PodHostnameBase

from . import TestCase


class GenericObjectBase(TestCase):
    @classmethod
    def setUpClass(self):
        self.env = pyrkube.config.ENVIRONMENT
        self.api = pyrkube.client.KubeAPIClient(env=self.env)

    @classmethod
    def tearDownClass(self):
        self.env = None
        self.api = None


class ObjectBase:
    base_adicts = ('metadata',)

    def setUp(self):
        self.objs = self.api.get(self._class.__name__)

    def tearDown(self):
        self.objs = None

    def test_create_and_type(self):
        for obj in self.objs:
            self.assertIsNotNone(obj)
            self.assertTrue(len(repr(obj)))
            self.assertIsInstance(obj, self._class)

    def test_correct_kind(self):
        for obj in self.objs:
            self.assertEqual(obj.kind, self._class.kind)

    def test_api_object_added(self):
        for obj in self.objs:
            self.assertIn('_api', obj)
            self.assertIsInstance(obj._api, pyrkube.client.KubeAPIClient)

    def test_object_properties_exist_and_correct_type(self):
        for obj in self.objs:
            for attr in self.base_adicts:
                self.assertIn(attr, obj)
                self.assertIsInstance(getattr(obj, attr), adict)
            for attr in ('apiVersion', 'kind'):
                self.assertTrue(hasattr(obj, attr))
                self.assertIsInstance(getattr(obj, attr), str)

    def test_metadata_default_adicts_created(self):
        for obj in self.objs:
            for attr in ('labels', 'annotations'):
                self.assertIn(attr, obj.metadata)
                self.assertIsInstance(getattr(obj.metadata, attr), adict)

    def test_annotation_references_deserialized(self):
        for obj in self.objs:
            if obj.metadata.annotations.get('kubernetes.io/created-by'):
                self.assertIsInstance(
                    obj.metadata.annotations['kubernetes.io/created-by'], adict
                )
                ref = obj.metadata.annotations[
                    'kubernetes.io/created-by'].reference
                self.assertIsNotNone(ref)
                self.assertIsInstance(ref, adict)
                self.assertIn('kind', ref)
                self.assertIsInstance(ref['kind'], str)

    def test_name_property_exists_is_string_and_not_empty(self):
        for obj in self.objs:
            self.assertTrue(hasattr(obj, 'name'))
            self.assertIsInstance(obj.name, str)
            self.assertTrue(len(obj.name))

    def test_sort_on_name(self):
        objs = sorted(self.objs.copy())
        for i in range(len(objs) - 1):
            self.assertLess(objs[i], objs[i + 1])

    def test_ready_property_exists_and_is_boolean(self):
        if hasattr(self, 'has_ready') and self.has_ready:
            for obj in self.objs:
                self.assertTrue(hasattr(obj, 'ready'))
                self.assertIsInstance(obj.ready, bool)


class TestPodObject(ObjectBase, GenericObjectBase):
    base_adicts = ('spec', 'status')
    _class = Pod
    has_ready = True

    def setUp(self):
        self.base_adicts = self.base_adicts + ObjectBase.base_adicts
        ObjectBase.setUp(self)

    def tearDown(self):
        self.base_adicts = None
        ObjectBase.tearDown(self)

    @staticmethod
    def _get_containers(obj):
        if hasattr(obj.spec, 'containers'):
            return obj.spec.containers
        elif hasattr(obj.spec.template.spec, 'containers'):
            return obj.spec.template.spec.containers

    @staticmethod
    def _get_volumes(obj):
        if hasattr(obj.spec, 'volumes'):
            return obj.spec.volumes
        elif hasattr(obj.spec.template.spec, 'volumes'):
            return obj.spec.template.spec.volumes

    def test_containers_exist_and_are_adict(self):
        for obj in self.objs:
            containers = self._get_containers(obj)

            self.assertIsNotNone(containers)
            self.assertIsInstance(containers, adict)
            self.assertGreater(len(list(containers.values())), 0)

            for container in containers.values():
                self.assertIsNotNone(container)
                self.assertIsInstance(container, Container)
                for attr in ('env', 'image', 'name', 'resources'):
                    self.assertIn(attr, container)

    def test_environment_created(self):
        for obj in self.objs:
            for container in self._get_containers(obj).values():
                self.assertIn('env', container)
                self.assertIsNotNone(container.env)
                self.assertIsInstance(container.env, ContainerEnv)

    def test_environment_resolved(self):
        for obj in self.objs:
            for container in self._get_containers(obj).values():
                for key, value in container.env.items():
                    self.assertIsNotNone(key)
                    self.assertIsInstance(key, str)
                    self.assertGreater(len(key), 0)

                    self.assertIsNotNone(value)
                    self.assertIsInstance(value, str)
                    self.assertGreater(len(value), 0)

    def test_volumes(self):
        for obj in self.objs:
            volumes = self._get_volumes(obj)
            if volumes:
                self.assertIsInstance(volumes, list)
                for volume in volumes:
                    self.assertIn('name', volume)
                    self.assertIsInstance(volume.name, str)
                    self.assertGreater(len(volume.name), 0)


class TestDeploymentObject(TestPodObject):
    _class = Deployment

    def test_pods(self):
        for obj in self.objs:
            self.assertTrue(hasattr(obj, 'pods'))
            self.assertIsInstance(obj.pods, list)
            for pod in obj.pods:
                self.assertIsNotNone(pod)
                self.assertIsInstance(pod, Pod)


class TestReplicaSetObject(TestDeploymentObject):
    _class = ReplicaSet


class TestStatefulSetObject(TestDeploymentObject):
    _class = StatefulSet


class TestSecret(ObjectBase, GenericObjectBase):
    base_adicts = ('data',)
    _class = Secret
    has_ready = False

    def setUp(self):
        self.base_adicts = self.base_adicts + ObjectBase.base_adicts
        ObjectBase.setUp(self)

    def tearDown(self):
        self.base_adicts = None
        ObjectBase.tearDown(self)

    def test_data(self):
        for obj in self.objs:
            for key, val in obj.data.items():
                self.assertIsNotNone(key)
                self.assertIsInstance(key, str)
                self.assertGreater(len(key), 0)

                self.assertIsNotNone(key)
                self.assertIsInstance(key, str)
                self.assertGreater(len(key), 0)

    def test_custom_get(self):
        for obj in self.objs:
            for key in obj.data.keys():
                val = obj.get(key)
                self.assertIsNotNone(val)
                self.assertIsInstance(key, str)
                self.assertGreater(len(key), 0)


class TestConfigMap(TestSecret):
    _class = ConfigMap


class TestEndpoint(ObjectBase, GenericObjectBase):
    # base_adicts = ('subsets',)
    _class = Endpoint
    has_ready = True

    def setUp(self):
        # self.base_adicts = self.base_adicts + ObjectBase.base_adicts
        ObjectBase.setUp(self)
        self.objs = [obj for obj in self.objs if obj.name != 'kubernetes']

    def tearDown(self):
        self.base_adicts = None
        ObjectBase.tearDown(self)

    def test_endpoint_properties(self):
        for obj in self.objs:
            for attr in ('subsets', 'addresses'):
                val = getattr(obj, attr)
                self.assertIsNotNone(val)
                self.assertIsInstance(val, list)

    def test_addresses(self):
        for obj in self.objs:
            addresses = obj.addresses
            self.assertIsNotNone(addresses)
            self.assertIsInstance(addresses, list)

    def test_each_address_endpoint_correct_type(self):
        for obj in self.objs:
            for address in obj.addresses:
                self.assertIsNotNone(address)
                self.assertIsInstance(address, EndpointAddress)

    def test_each_address_endpoint_has_endpoint_reference(self):
        for obj in self.objs:
            for address in obj.addresses:
                self.assertIsNotNone(address._endpoint)
                self.assertIsInstance(address._endpoint, Endpoint)

    def test_each_address_endpoint_has_target_reference(self):
        for obj in self.objs:
            for address in obj.addresses:
                self.assertIsNotNone(address.targetRef)
                self.assertIsInstance(address.targetRef, adict)

    def test_address_endpoint_properties(self):
        for obj in self.objs:
            for address in obj.addresses:
                for attr in ('ip', 'nodeName'):
                    self.assertTrue(hasattr(address, attr))
                    val = getattr(address, attr)
                    self.assertIsNotNone(val)
                    self.assertIsInstance(val, str)

    def test_address_endpoint_targets(self):
        for obj in self.objs:
            for address in obj.addresses:
                target = address.target
                self.assertIsNotNone(target)
                self.assertIsInstance(target, Pod)

    def test_endpoint_pods(self):
        for obj in self.objs:
            pods = obj.pods
            for pod in pods:
                self.assertIsNotNone(pod)
                self.assertIsInstance(pod, Pod)
            for i in range(len(pods) - 1):
                self.assertLess(pods[i], pods[i + 1])

    def test_endpoint_nodes(self):
        for obj in self.objs:
            nodes = obj.nodes
            for node in nodes:
                self.assertIsNotNone(node)
                self.assertIsInstance(node, str)
                self.assertGreater(len(node), 0)

            # for i in range(len(nodes) - 1):
            #     self.assertLess(nodes[i], nodes[i + 1])

    def test_endpoint_ips(self):
        for obj in self.objs:
            ips = obj.ips
            for ip in ips:
                self.assertIsNotNone(ip)
                self.assertIsInstance(ip, str)
                self.assertGreater(len(ip), 0)

            for i in range(len(ips) - 1):
                self.assertLess(ips[i], ips[i + 1])

    def test_endpoint_hosts(self):
        for obj in self.objs:
            hosts = obj.hosts
            for host in hosts:
                self.assertIsNotNone(host)
                self.assertIsInstance(host, str)
                self.assertGreater(len(host), 0)

            for i in range(len(hosts) - 1):
                self.assertLess(hosts[i], hosts[i + 1])

    def test_endpoint_hostnames(self):
        for obj in self.objs:
            hostnames = obj.hostnames
            for hostname in hostnames:
                self.assertIsNotNone(hostname)
                self.assertIsInstance(hostname, PodHostnameBase)
                self.assertGreater(len(str(hostname)), 0)

            for i in range(len(hostnames) - 1):
                self.assertLess(hostnames[i], hostnames[i + 1])


class TestService(ObjectBase, GenericObjectBase):
    base_adicts = ('spec', 'status')
    _class = Service
    has_ready = False

    def test_has_endpoint(self):
        for obj in self.objs:
            ep = obj.endpoint
            self.assertIsNotNone(ep)
            self.assertIsInstance(ep, Endpoint)


class TestKubeApp(GenericObjectBase):
    def setUp(self):
        GenericObjectBase.setUp(self)
        self.objs = [
            KubeApp(self.api, name) for name in ('couchdb', 'rabbitmq')]

    def tearDown(self):
        GenericObjectBase.tearDown(self)
        self.objs = None

    def test_created_and_correct_type(self):
        for obj in self.objs:
            self.assertIsNotNone(obj)
            self.assertIsInstance(obj, KubeApp)
            self.assertGreater(len(repr(obj)), 0)

    def has_correct_api_object(self):
        for obj in self.objs:
            api = getattr(obj, 'api')
            self.assertTrue(api)
            self.assertIsInstance(obj._api, pyrkube.client.KubeAPIClient)

    def test_object_attributes_set_correct_type_and_value(self):
        for obj in self.objs:
            self.assertTrue(hasattr(obj, 'name'))
            self.assertIsInstance(obj.name, str)
            self.assertGreater(len(obj.name), 0)

            self.assertTrue(hasattr(obj, 'sleep'))
            self.assertIsInstance(obj.sleep, int)
            self.assertGreater(obj.sleep, 0)

    def test_kind(self):
        for obj in self.objs:
            self.assertTrue(obj.kind)
            self.assertIsNotNone(obj.kind)
            self.assertIsInstance(obj.kind, str)
            self.assertIn(obj.kind, ('Deployment', 'StatefulSet'))

    def test_resource(self):
        for obj in self.objs:
            self.assertTrue(obj.resource)
            self.assertIsNotNone(obj.resource)
            self.assertIsInstance(obj.resource, ResourceBase)
            self.assertIn(type(obj.resource).__name__,
                          ('Deployment', 'StatefulSet'))

    def test_loaded(self):
        for obj in self.objs:
            self.assertIsNotNone(obj.loaded)
            self.assertIsInstance(obj.loaded, bool)

    def test_ready(self):
        for obj in self.objs:
            self.assertIsNotNone(obj.ready)
            self.assertIsInstance(obj.ready, bool)


class TestKubeApps(GenericObjectBase):
    def setUp(self):
        GenericObjectBase.setUp(self)
        self.names = ('couchdb', 'rabbitmq')
        self.obj = KubeApps(self.api, self.names, logger='tests')

    def tearDown(self):
        GenericObjectBase.tearDown(self)
        self.names = None
        self.obj = None

    def test_api_is_set_and_correct_class(self):
        self.assertTrue(hasattr(self.obj, 'api'))
        self.assertIsInstance(self.obj.api, pyrkube.client.KubeAPIClient)

    def test_attributes_set_and_correct_type(self):
        self.assertTrue(hasattr(self.obj, 'names'))
        self.assertIsInstance(self.obj.names, tuple)

        self.assertTrue(hasattr(self.obj, 'logging'))
        self.assertIsInstance(self.obj.logging, bool)

        if self.obj.logging:
            self.assertIsInstance(self.obj.logger, logging.Logger)

        self.assertTrue(hasattr(self.obj, 'sleep'))
        self.assertTrue(self.obj.sleep, int)

    def test_get_app_returns_app(self):
        app = self.obj._get_app('rabbitmq')
        self.assertIsNotNone(app)
        self.assertIsInstance(app, KubeApp)
        self.assertEqual(app.name, 'rabbitmq')

    def test_apps_loaded(self):
        self.assertIsNotNone(self.obj.apps)
        self.assertIsInstance(self.obj.apps, dict)
        self.assertIs(self.obj.apps, self.obj._wrapped)

    def test_ready_is_correct(self):
        self.assertTrue(hasattr(self.obj, 'ready'))
        self.assertIsInstance(self.obj.ready, bool)

    def test_status(self):
        self.assertIsInstance(self.obj.status, dict)
        self.assertListEqual(
            sorted(self.obj.status.keys()),
            sorted(self.obj.names)
        )
        for key, val in self.obj.status.items():
            self.assertIsNotNone(key)
            self.assertIsInstance(key, str)

            self.assertIsNotNone(val)
            self.assertIsInstance(val, bool)

    def test_wait_emits_logs(self):
        with self.assertLogs('tests', level='INFO') as cm:
            self.obj.wait()
            self.assertGreater(len(cm.output), 0)

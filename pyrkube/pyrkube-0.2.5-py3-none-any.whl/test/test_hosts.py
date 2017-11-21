import pyrkube
from pyrkube.hosts import get_hostname, PodHostname, StatefulPodHostname

from . import TestCase


class TestPodHostsFromString(TestCase):
    def setUp(self):
        self.ip = '172.16.16.223'
        self.hostname = self.ip.replace('.', '-')
        self.namespace = 'default'
        self.domain = 'cluster.local'
        self.hostname_str = '%s.%s.pod.%s' % (
            self.hostname, self.namespace, self.domain
        )

    def tearDown(self):
        self.ip = None
        self.hostname = None
        self.namespace = None
        self.domain = None
        self.hostname_str = None

    def test_create(self):
        h = get_hostname(self.hostname_str)
        self.assertTrue(repr(h))
        self.assertEqual(type(h), PodHostname)

    def test_properties(self):
        h = get_hostname(self.hostname_str)

        self.assertEqual(h.ip, self.ip)
        self.assertEqual(h.hostname, self.hostname)
        self.assertEqual(h.namespace, self.namespace)
        self.assertEqual(h.domain, self.domain)
        self.assertEqual(h.fqdn, self.hostname_str)

    def test_string_conversion(self):
        h = get_hostname(self.hostname_str)

        self.assertEqual(type(str(h)), str)
        self.assertEqual(str(h), self.hostname_str)

    def test_clone(self):
        h1 = get_hostname(self.hostname_str)
        h2 = h1.clone()
        self.assertEqual(repr(h1), repr(h2))
        self.assertEqual(str(h1), str(h2))

    def test_sort(self):
        hosts = [get_hostname('172-17-0-%d.default.pod.cluster.local' % i)
                 for i in range(3, 0, -1)]

        self.assertFalse(
            str(hosts[0]) < str(hosts[1]) < str(hosts[2])
        )

        hosts = sorted(hosts)
        self.assertTrue(
            str(hosts[0]) < str(hosts[1]) < str(hosts[2])
        )


class TestPodHostsFromPod(TestCase):
    def setUp(self):
        self.env = pyrkube.config.ENVIRONMENT
        self.api = pyrkube.client.KubeAPIClient(
            env=self.env, namespace='default', domain='cluster.local')
        self.ep = self.api.get('endpoint', 'rabbitmq')
        self.pods = self.ep.pods

    def tearDown(self):
        self.env = None
        self.api = None
        self.ep = None
        self.pods = None

    def test_create(self):
        for pod in self.pods:
            h = pyrkube.hosts.get_hostname(pod)
            self.assertTrue(repr(h))
            self.assertEqual(type(h), PodHostname)

    def test_properties(self):
        for pod in self.pods:
            h = pyrkube.hosts.get_hostname(pod)
            ip = pod.status.podIP
            hostname = ip.replace('.', '-')
            namespace = pod.metadata.namespace
            domain = 'cluster.local'
            fqdn = '%s.%s.pod.%s' % (hostname, namespace, domain)

            self.assertEqual(h.ip, ip)
            self.assertEqual(h.hostname, hostname)
            self.assertEqual(h.namespace, namespace)
            self.assertEqual(h.domain, domain)
            self.assertEqual(h.fqdn, fqdn)

    def test_string_conversion(self):
        for pod in self.pods:
            h = pyrkube.hosts.get_hostname(pod)
            ip = pod.status.podIP
            hostname = ip.replace('.', '-')
            namespace = pod.metadata.namespace
            domain = 'cluster.local'
            fqdn = '%s.%s.pod.%s' % (hostname, namespace, domain)
            self.assertTrue(repr(h))

            self.assertEqual(type(str(h)), str)
            self.assertEqual(str(h), fqdn)

    def test_clone(self):
        for pod in self.pods:
            h1 = pyrkube.hosts.get_hostname(pod)

            h2 = h1.clone()
            self.assertEqual(repr(h1), repr(h2))
            self.assertEqual(str(h1), str(h2))


class TestStatefulHostsFromString(TestCase):
    def setUp(self):
        self.index = 0
        self.statefulset = 'couchdb'
        self.hostname = '%s-%d' % (self.statefulset, self.index)
        self.subdomain = 'couchdb'
        self.namespace = 'default'
        self.domain = 'cluster.local'
        self.hostname_str = '%s.%s.%s.svc.%s' % (
            self.hostname, self.subdomain, self.namespace, self.domain
        )
        self.host = get_hostname(self.hostname_str)

    def tearDown(self):
        self.index = None
        self.statefulset = None
        self.hostname = None
        self.subdomain = None
        self.namespace = None
        self.domain = None
        self.hostname_str = None
        self.host = None

    def test_create(self):
        h = get_hostname(self.hostname_str)
        self.assertTrue(repr(h))
        self.assertEqual(type(h), StatefulPodHostname)

    def test_properties(self):
        h = self.host
        self.assertEqual(h.index, self.index)
        self.assertEqual(h.statefulset, self.statefulset)
        self.assertEqual(h.hostname, self.hostname)
        self.assertEqual(h.subdomain, self.subdomain)
        self.assertEqual(h.namespace, self.namespace)
        self.assertEqual(h.domain, self.domain)
        self.assertEqual(h.fqdn, self.hostname_str)

    def test_string_conversion(self):
        h = self.host

        self.assertEqual(type(str(h)), str)
        self.assertEqual(str(h), self.hostname_str)

    def test_clone(self):
        h1 = self.host
        h2 = h1.clone()
        self.assertEqual(repr(h1), repr(h2))
        self.assertEqual(str(h1), str(h2))

        h3 = h1.clone(index=1)
        self.assertEqual(h3.index, 1)
        h4 = h3.clone(master=True)
        self.assertEqual(h4.index, 0)

    def test_sort(self):
        hosts = [self.host.clone(index=i) for i in range(3, 0, -1)]
        self.assertFalse(
            str(hosts[0]) < str(hosts[1]) < str(hosts[2])
        )
        hosts = sorted(hosts)
        self.assertTrue(
            str(hosts[0]) < str(hosts[1]) < str(hosts[2])
        )

    def test_is_master(self):
        h = self.host
        self.assertTrue(h.is_master)
        h2 = h.clone(index=1)
        self.assertFalse(h2.is_master)


class TestStatefulHostFromPod(TestCase):
    def setUp(self):
        self.env = pyrkube.config.ENVIRONMENT
        self.api = pyrkube.client.KubeAPIClient(
            env=self.env, namespace='default', domain='cluster.local')
        self.ep = self.api.get('endpoint', 'couchdb')
        self.pods = self.ep.pods

        self.statefulset = 'couchdb'
        self.subdomain = 'couchdb'
        self.namespace = 'default'
        self.domain = 'cluster.local'

    def tearDown(self):
        self.env = None
        self.api = None
        self.ep = None
        self.pods = None

        self.statefulset = None
        self.subdomain = None
        self.namespace = None
        self.domain = None

    def test_create(self):
        for pod in self.pods:
            h = get_hostname(pod)
            self.assertTrue(repr(h))
            self.assertEqual(type(h), StatefulPodHostname)

    def test_properties(self):
        for pod in self.pods:
            h = get_hostname(pod)
            ip = pod.status.podIP
            index = int(pod.metadata.name.split('-')[1])
            hostname = '%s-%d' % (self.statefulset, index)

            fqdn = '%s-%d.%s.%s.svc.%s' % (
                self.statefulset,
                index,
                self.subdomain,
                self.namespace,
                self.domain
            )
            self.assertEqual(h.ip, ip)
            self.assertEqual(h.index, index)
            self.assertEqual(h.statefulset, self.statefulset)
            self.assertEqual(h.hostname, hostname)
            self.assertEqual(h.subdomain, self.subdomain)
            self.assertEqual(h.namespace, self.namespace)
            self.assertEqual(h.domain, self.domain)
            self.assertEqual(h.fqdn, fqdn)

    def test_string_conversion(self):
        for pod in self.pods:
            h = get_hostname(pod)
            index = int(pod.metadata.name.split('-')[1])

            fqdn = '%s-%d.%s.%s.svc.%s' % (
                self.statefulset,
                index,
                self.subdomain,
                self.namespace,
                self.domain
            )

            self.assertEqual(type(str(h)), str)
            self.assertEqual(str(h), fqdn)

    def test_clone(self):
        for pod in self.pods:
            h1 = get_hostname(pod)

            h2 = h1.clone()
            self.assertEqual(repr(h1), repr(h2))
            self.assertEqual(str(h1), str(h2))

            h3 = h1.clone(index=1)
            self.assertEqual(h3.index, 1)
            h4 = h3.clone(master=True)
            self.assertEqual(h4.index, 0)

    def test_sort(self):
        hosts = self.ep.hostnames
        self.assertTrue(
            str(hosts[0]) < str(hosts[1]) < str(hosts[2])
        )

    def test_is_master(self):
        for pod in self.pods:
            h = get_hostname(pod)
            index = int(pod.metadata.name.split('-')[1])

            if index == 0:
                self.assertTrue(h.is_master)
            else:
                self.assertFalse(h.is_master)

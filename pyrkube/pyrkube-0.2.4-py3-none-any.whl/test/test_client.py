import types

import pyrkube

from . import TestCase


class TestClient(TestCase):

    def setUp(self):
        self.env = pyrkube.config.ENVIRONMENT
        self.api = pyrkube.client.KubeAPIClient(
            env=self.env, namespace='default', domain='cluster.local')

    def tearDown(self):
        self.env = None
        self.api = None

    def test_client_setup(self):
        """
        Test Config instance creation.
        """
        api = self.api
        self.assertIn(api.env, ('test', 'dev'))
        self.assertEqual(api.cluster, 'minikube')
        self.assertEqual(api.namespace, 'default')

        self.assertEqual(api.domain, 'cluster.local')
        self.assertEqual(api.user, 'minikube')
        self.assertTrue(api.server.startswith('https://'))

    def test_get_by_name(self):
        pods = self.api.get('pod')
        name = pods[0].name

        pod = self.api.get('pod', name)
        self.assertIsNotNone(pod)
        self.assertIsInstance(pod, pyrkube.objects.Pod)

    def test_get_by_selector(self):
        pods = self.api.get('pod')
        selector = dict(pods[0].metadata.labels)

        pods = self.api.get('pod', selector=selector)
        self.assertIsNotNone(pods)
        self.assertIsInstance(pods, list)
        self.assertGreater(len(pods), 0)

        for pod in pods:
            self.assertIsNotNone(pod)
            self.assertIsInstance(pod, pyrkube.objects.Pod)

    def test_get_watch(self):

        pods = self.api.get('pod')
        selector = dict(pods[0].metadata.labels)

        watch = self.api.get('pod', selector=selector, watch=True)

        self.assertIsNotNone(watch)
        self.assertIsInstance(watch, types.GeneratorType)

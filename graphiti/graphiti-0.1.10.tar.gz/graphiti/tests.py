import time
from socket import socket, SO_REUSEADDR, SOL_SOCKET, SHUT_RDWR, error
from threading import Thread, Event
from graphiti import Client, Aggregator, timeit, ClientPlainText
from unittest import TestCase
from contextlib import contextmanager
from pickle import loads
from struct import unpack


SERVER_HOST = "localhost"
SERVER_PORT = 56780


class ServerLoop(Thread):

    def __init__(self, group=None, target=None, name="ServerLoop",
                 args=(), kwargs=None, verbose=None):
        super(ServerLoop, self).__init__(group, target, name, args, kwargs)
        self.server_run = Event()
        self.server_stopped = Event()
        self.server_stopped.set()
        self.metrics = []
        self.message = b""

    def _receive(self, client, length):
        try:
            self.message += client.recv(length)
        except error:
            pass

    def receive(self, client, length):
        while len(self.message) < length and self.server_run.is_set():
            self._receive(client, length)
            time.sleep(0.1)

        if len(self.message) >= length:
            res = self.message[:length]
            self.message = self.message[length:]
            return res
        else:
            return None

    def run(self):
        server_socket = socket()
        server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        server_socket.settimeout(1)
        server_socket.bind((SERVER_HOST, SERVER_PORT))
        server_socket.listen(5)
        self.server_run.set()

        client, address = None, None
        while self.server_run.is_set():
            try:
                client, address = server_socket.accept()
            except error:
                time.sleep(0.0001)
            else:
                client.setblocking(0)
                break

        while self.server_run.is_set():
            msg_len = self.receive(client, 4)
            if msg_len is None:
                break
            length = unpack("!L", msg_len)[0]
            metrics = self.receive(client, length)
            if metrics is None:
                break
            self.metrics.extend(loads(metrics))

        server_socket.close()

        if client:
            client.shutdown(SHUT_RDWR)
            client.close()


class TestGraphiti(TestCase):

    def run_server(self):
        self.stop_server()
        self.server = ServerLoop()
        self.server.daemon = True
        self.server.start()
        self.server.server_run.wait()

    def stop_server(self):
        if hasattr(self, "server") and self.server:
            self.server.server_run.clear()
            self.server.join()

    def setUp(self):
        super(TestGraphiti, self).setUp()
        self.run_server()
        self.client = Client(SERVER_HOST, SERVER_PORT, verbose=True)

    def tearDown(self):
        super(TestGraphiti, self).tearDown()
        self.client.stop()
        self.stop_server()

    def retries(self, timeout=5, sleep_time=0.5, exception=AssertionError, sleep=time.sleep):
        timeout_at = time.time() + timeout
        state = {"fails_count": 0, "give_up": False, "success": False}
        while time.time() < timeout_at:
            yield self.handler(exception, state)
            if state["success"]:
                return
            sleep(sleep_time)
        state["give_up"] = True
        yield self.handler(exception, state)

    @contextmanager
    def handler(self, exception, state):
        try:
            yield
        except exception:
            state["fails_count"] += 1
            if state["give_up"]:
                raise
        else:
            state["success"] = True

    def test_base_plain(self):
        client = ClientPlainText(SERVER_HOST, SERVER_PORT)

        client.send('path', 1, time.time())
        client.send(['path1', 'path2'], 2, time.time())
        client.send(['path3'], 3)

    def test_base(self):
        self.client.send('path', 1, time.time())
        self.client.send(['path1', 'path2'], 2, time.time())
        self.client.send(['path3'], 3)

    def test_send_message_with_flush(self):
        self.client.send('path', 4, time.time())
        self.assertEqual(len(self.client.messages), 1)

        self.client.flush(timeout=1)
        self.assertEqual(len(self.client.messages), 0)

        self.client.send('path', 3, time.time())

        self.client.flush()
        self.assertEqual(len(self.client.messages), 0)

    def test_worker(self):
        self.client.batch([('path', 2, time.time()) for _ in range(3000)])
        time.sleep(0.1)
        for attempt in self.retries(timeout=2):
            with attempt:
                self.assertEqual(len(self.client.messages), 0)

    def test_fail_rise(self):
        self.stop_server()

        self.client.batch([('path', 1, time.time()) for _ in range(3000)])
        self.assertEqual(len(self.client.messages), 3000)

        self.run_server()
        for attempt in self.retries(timeout=3):
            with attempt:
                self.assertEqual(len(self.client.messages), 0)

    def test_rise_fail(self):
        self.client.batch([('path', 5, 'timestamp') for _ in range(3000)])
        for attempt in self.retries(timeout=3, sleep_time=0.1):
            with attempt:
                self.assertEqual(len(self.client.messages), 0)

        self.stop_server()

        self.client.batch([('path', 6, 'timestamp') for _ in range(30020)])
        time.sleep(1.)
        self.assertGreater(len(self.client.messages), 0)

    def test_aggregator(self):

        agg = Aggregator(self.client, interval=2)

        n = 14
        for x in range(n):
            agg.add_count("count")
            agg.add_sum("sum", x)
            agg.add_avg("average", x)
        agg.add_active("up")

        for attempt in self.retries(5):
            with attempt:
                self.assertTrue(self.server.metrics)
                metrics = {name: value for name, (_, value) in self.server.metrics}
                self.assertEqual(int(metrics["sum"]), (0 + n - 1) * n / 2)
                self.assertEqual(int(metrics["up"]), 1)
                self.assertEqual(int(metrics["count"]), n)
                self.assertEqual(metrics["average"], (0 + n - 1) / 2.)
                self.server.metrics = []

        agg.add_count("count")

        for attempt in self.retries(5):
            with attempt:
                metrics = dict((name, value) for name, (_, value) in self.server.metrics)
                self.assertEqual(len(self.server.metrics), 1)
                self.assertEqual(int(metrics["count"]), 1)

        agg.stop()

    def test_timeit(self):

        agg = Aggregator(self.client, 1)
        start = time.time()
        with timeit(agg, "test1.test2"):
            time.sleep(0.1)
        work_time = time.time() - start

        for attempt in self.retries(2):
            with attempt:
                metrics = dict((name, value) for name, (_, value) in self.server.metrics)
                self.assertTrue(metrics)
                self.assertEqual(metrics['test1.test2.count'], 1)
                self.assertAlmostEqual(metrics['test1.test2.time_sum'], work_time*1000., delta=1)
                self.assertAlmostEqual(metrics['test1.test2.time_avg'], work_time*1000., delta=1)
                self.server.metrics = []

        agg.stop()
        agg = Aggregator(self.client, 3)

        start = time.time()
        for x in range(5):
            with timeit(agg, ["test3", "test4"]):
                time.sleep(0.1)
        work_time = (time.time() - start)

        for attempt in self.retries(5):
            with attempt:
                metrics = dict((name, value) for name, (_, value) in self.server.metrics)
                self.assertTrue(metrics)
                self.assertEqual(metrics['test3.test4.count'], 5)
                self.assertAlmostEqual(metrics['test3.test4.time_sum'], work_time * 1000, delta=10)
                self.assertAlmostEqual(metrics['test3.test4.time_avg'], work_time * 1000 / 5, delta=2)
                self.server.metrics = []

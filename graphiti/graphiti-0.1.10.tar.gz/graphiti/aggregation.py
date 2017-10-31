# -*- coding: utf-8 -*-
from threading import RLock, Event, Thread
import logging
import contextlib
import time
from .client import normalize_path


class MetricSum(object):
    """ Base metric class implementing simple summation of values
    """

    def __init__(self):
        self.value_sum = 0.0
        self.value_count = 0.0

    def update(self, value):
        """ Called when new value is passed
        """
        self.value_sum += value
        self.value_count += 1

    def clear(self):
        """ Called after metric is sent
        """
        self.value_count = self.value_sum = 0.0

    def calculate(self):
        """ Called when right before sending
        """
        return self.value_sum


class MetricAvg(MetricSum):
    def calculate(self):
        if self.value_count:
            return float(self.value_sum) / self.value_count
        return 0.0


class MetricActive(MetricSum):
    def update(self, value):
        self.value_sum = 1.0
        self.value_count = 1.0


class Aggregator(object):

    GRAPHITE_FLUSH_TIMEOUT = 0.1
    POOL_TIMEOUT = 1.0

    def __init__(self, graphite_client, interval=60, logger=None):
        """
        Helper for graphite client for aggregating metrics.
        It aggregates metrics and sends them once in an `interval` seconds.
        You can optionally pass `logger` instance.

        :param graphite_client: Graphite client
        :param interval: aggregation interval in second
        :param logger: Logger object. By default the logging will be graphite.aggregator logger

        For example, if you need to send metric 'processed_messages' once in a minute::

            client = GraphiteClient(...)
            aggregator = GraphiteAggregator(client, 60)

            while True:
                process_message(...)
                # ...
                aggregator.add_sum('processed_messages', 1)
                aggregator.add_avg('message_processing_avg_time', time_taken)
                aggregator.add_active('service_is_up')

        Be aware, that aggregator is runs in separate thread.
        """
        self._metrics = {}
        self.graphite_client = graphite_client
        self.interval = interval
        self.message_lock = RLock()
        self.logger = logger or logging.getLogger("graphiti.aggregator")

        self._stop = Event()
        self.worker = Thread(target=self.worker_loop, name="GraphitiAggregator")
        self.worker.daemon = True
        self.worker.start()

    def add_sum(self, metric_path, value):
        self.add_metric(metric_path, value, MetricSum)

    def add_avg(self, metric_path, value):
        self.add_metric(metric_path, value, MetricAvg)

    def add_count(self, metric_path, value=1):
        self.add_sum(metric_path, value)

    def add_active(self, metric_path):
        self.add_metric(metric_path, 1, MetricActive)

    def add_metric(self, metric_path, value, metric_class):
        """ Add value to metric with custom aggregation class `metric_class`
        """
        with self.message_lock:
            metric = self._metrics.get(metric_path)
            if metric is None:
                self._metrics[metric_path] = metric = metric_class()
            metric.update(value)

    def remove_metric(self, metric_path):
        """ Removes metric, note that aggregator will not send pending values
        """
        with self.message_lock:
            self._metrics.pop(metric_path, None)

    def worker_loop(self):
        next_send = time.time() + self.interval
        pool_timeout = min(self.POOL_TIMEOUT, self.interval)
        while not self._stop.is_set():
            if time.time() < next_send:
                self._stop.wait(pool_timeout)
                continue

            try:
                self._send_all_metrics()
            except Exception as e:
                self.logger.exception("Exception during sending metrics: %s" % e)
            next_send = time.time() + self.interval

    def _send_all_metrics(self):
        import six
        self.logger.info("Sending %s aggregated metrics", len(self._metrics))
        with self.message_lock:
            for metric_path, metric in six.iteritems(self._metrics):
                if metric.value_count:
                    self.graphite_client.send(metric_path, metric.calculate())
                    metric.clear()
            self.graphite_client.flush(self.GRAPHITE_FLUSH_TIMEOUT)

    def stop(self):
        """ Gracefully stops aggregator
        """
        with self.message_lock:
            self._send_all_metrics()
            self.graphite_client.flush(self.GRAPHITE_FLUSH_TIMEOUT)
        self._stop.set()


@contextlib.contextmanager
def timeit(aggregator_client, metric_path, time_multiplier=1000, separator='.'):
    """ Context manager for measuring time of some operation

    :param aggregator_client:  Aggregator client
    :param metric_path: Metric path
    :param time_multiplier: factor for time duration. The default value is 1000, i.e. metrics are in milliseconds
    :param separator: Metric name separator

        Example::
            with timeit(aggregator, "some_work"):
                do_some_work()

        It will measure time of operations in context and then add three metrics:

            - xxx.time_avg - average time
            - xxx.time_sum - total time
            - xxx.count -   number of measures
    """
    start = time.time()
    try:
        yield
    finally:
        if aggregator_client:
            duration = (time.time() - start) * time_multiplier
            metric_path = normalize_path(metric_path) + separator

            aggregator_client.add_avg("%stime_avg" % metric_path, duration)
            aggregator_client.add_sum("%stime_sum" % metric_path, duration)
            aggregator_client.add_count("%scount" % metric_path)

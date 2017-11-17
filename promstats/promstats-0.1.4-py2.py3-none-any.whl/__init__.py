from functools import partial
import logging
import os
import sys

from prometheus_client import CollectorRegistry, Gauge, Histogram, Counter,\
    Summary, pushadd_to_gateway, push_to_gateway

from ._timer import Timer
from ._util import maybe_labels, tags_to_labels


logger = logging.getLogger(__name__)
_version_info = sys.version_info
_PY_35 = _version_info.major >= 3 and _version_info.minor >= 5


class Stats:
    """A stats collector instance, used for collecting the metrics."""

    pushgateway_uri = os.environ.get(
        'PROMSTATS_PUSHGATEWAY_URI',
        'http://localhost:9112',
    )

    def __init__(
            self,
            job_name,
            pushgateway_handler=None,
            pushgateway_uri=None):
        """
        :param job_name (str): A Prometheus job name.
        :param gateway_handler (function): Optional custom handler
            for gateway push.
        :param pushgateway_uri: An optional pushgateway URI to use.
        """
        self.job_name = job_name
        self.registry = CollectorRegistry()
        self.metrics = {}
        self.pushgateway_handler = pushgateway_handler
        if pushgateway_uri:
            self.pushgateway_uri = pushgateway_uri

    def _get_or_create_metric(self,
                              metric_name, metric_type, tags, verbose_name):
        """Get or create metric.

        :param metric_name (str): A metric name to use in scraper.
        :param metric_type (class): A metric type to instantiate.
        :param tags (list): An initial list of tags to pass to metric.
        :param verbose_name (str): A metric verbose name.
        """
        metric = self.metrics.get(metric_name)
        if metric is None:
            metric = metric_type(
                metric_name,
                verbose_name,
                tuple(tags_to_labels(tags).keys()),
                registry=self.registry,
            )
            self.metrics[metric_name] = metric
        return metric

    def increment(self, metric_name, tags=(), verbose_name='', value=1):
        """Increment the counter.

        :param metric_name (str): A metric name string.
        :param tags(list[str]): A list of tags to scrape.
        :param verbose_name: A metric verbose name.
        """
        metric = self._get_or_create_metric(
            metric_name, Counter, tags, verbose_name)
        maybe_labels(metric, tags).inc(value)

    def gauge(self, metric_name, value, tags=(), verbose_name=''):
        """Register a gauge, an arbitrary numeric value.

        :param metric_name (str): A metric name string.
        :param tags(list[str]): A list of tags to scrape.
        :param verbose_name: A metric verbose name.
        """
        metric = self._get_or_create_metric(
            metric_name, Gauge, tags, verbose_name)
        maybe_labels(metric, tags).set(value)

    def summary(self, metric_name, value, tags=(), verbose_name=''):
        """Register a gauge - an array of arbitrary numeric values.

        :param metric_name (str): A metric name string.
        :param tags(list[str]): A list of tags to scrape.
        :param verbose_name: A metric verbose name.
        """
        metric = self._get_or_create_metric(
            metric_name, Summary, tags, verbose_name)
        maybe_labels(metric, tags).observe(value)

    def histogram(self, metric_name, value, tags=(), verbose_name=''):
        """Register a histogram metric.

        :param metric_name (str): A metric name string.
        :param tags(list[str]): A list of tags to scrape.
        :param verbose_name: A metric verbose name.
        """
        metric = self._get_or_create_metric(
            metric_name, Histogram, tags, verbose_name)
        maybe_labels(metric, tags).observe(value)

    def timed(self, metric_name, tags=(), verbose_name=''):
        """A timing decorator/context manager, resulting into
            histogram of timings.

        :param metric_name (str): A metric name string.
        :param tags(list[str]): A list of tags to scrape.
        :param verbose_name: A metric verbose name.
        :returns Timer: A Timer instance, used for monitoring code execution.
        """

        metric = self._get_or_create_metric(
            metric_name, Histogram, tags, verbose_name)
        return Timer(metric, tags=tags)

    def _push(self, pusher_func):
        pusher = partial(pusher_func,
                         self.pushgateway_uri,
                         job=self.job_name,
                         registry=self.registry)
        if self.pushgateway_handler:
            pusher = partial(pusher, handler=self.pushgateway_handler)
        pusher()

    def push(self):
        """Push metrics to the gateway."""
        self._push(pusher_func=pushadd_to_gateway)

    def pushadd(self):
        """PushAdd metrics to the gateway."""
        self._push(pusher_func=push_to_gateway)

    if _PY_35:

        def asynctimed(self, metric_name, tags=(), verbose_name=''):
            """An asynchronous timing decorator.

            Wrap it around awaitable function, to get timing of its usage.

            :param metric_name (str): A metric name string.
            :param tags(list[str]): A list of tags to scrape.
            :param verbose_name: A metric verbose name.
            :returns AsyncTimer: An async Timer instance,
                used for monitoring execution time of coroutines.
            """
            from ._async import AsyncTimer
            metric = self._get_or_create_metric(
                metric_name, Histogram, tags, verbose_name)
            return AsyncTimer(metric, tags=tags)


__all__ = ['Stats', ]

import copy
import multiprocessing
from queue import Queue

from fizzgun.core.common import Input, Output
from fizzgun.core.deployment import FizzgunDeployment


class QueueConnector(Input, Output):
    def __init__(self, queue_class):
        self._q = queue_class()

    def pull(self):
        return self._q.get()

    def push(self, result):
        self._q.put_nowait(copy.deepcopy(result))


class QueueDeployment(FizzgunDeployment):
    """Runs a full stack of nodes connected by python queues"""

    def __init__(self, context, config):
        super(QueueDeployment, self).__init__(context, config, requires_dispatcher=False)

        queue_class = multiprocessing.Queue if config['stack'].get('use_processes', True) else Queue

        self._producer_output = QueueConnector(queue_class)
        self._q_filter_transformer = QueueConnector(queue_class)
        self._q_transformer_requestor = QueueConnector(queue_class)
        self._q_requestor_assertor = QueueConnector(queue_class)
        self._q_assertor_reporter = QueueConnector(queue_class)

    @property
    def producer_output(self):
        return self._producer_output

    @property
    def filter_connectors(self):
        return self._producer_output, self._q_filter_transformer

    @property
    def transformer_connectors(self):
        return self._q_filter_transformer, self._q_transformer_requestor

    @property
    def dispatcher_connectors(self):
        return None, None

    @property
    def requestor_connectors(self):
        return self._q_transformer_requestor, self._q_requestor_assertor

    @property
    def assertor_connectors(self):
        return self._q_requestor_assertor, self._q_assertor_reporter

    @property
    def reporter_connectors(self):
        return self._q_assertor_reporter, None

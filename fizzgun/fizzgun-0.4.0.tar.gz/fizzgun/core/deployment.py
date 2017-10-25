import multiprocessing
from threading import Thread
from typing import Tuple

from fizzgun.application.service_contexts import CmdRunFizzgunContext
from fizzgun.config import Config
from fizzgun.core import Filter, Transformer, Dispatcher, Requestor, Assertor, Reporter
from fizzgun.core.common import Input, Output


class FizzgunDeployment(object):
    def __init__(self, context: CmdRunFizzgunContext, config: Config, requires_dispatcher=False):
        self._ctx = context
        self._cfg = config
        self._processes = None
        self._use_dispatcher = requires_dispatcher
        self._async_class = multiprocessing.Process if config['stack'].get('use_processes', True) else Thread

    def start(self) -> Output:
        self._processes = []

        transformer_count = self._cfg['stack']['transformers']
        requestor_count = self._cfg['stack']['requestors']

        self._run_async(self._start_reporter)
        self._run_async(self._start_assertor)

        for x in range(requestor_count):
            self._run_async(self._start_requestor)

        if self._use_dispatcher:
            self._run_async(self._start_dispatcher)

        for x in range(transformer_count):
            self._run_async(self._start_transformer)

        self._run_async(self._start_filter)

        return self.producer_output

    @property
    def producer_output(self) -> Output:
        raise NotImplementedError("must be implemented in class '%s'" % self.__class__.__name__)

    @property
    def filter_connectors(self) -> Tuple[Input, Output]:
        raise NotImplementedError("must be implemented in class '%s'" % self.__class__.__name__)

    @property
    def transformer_connectors(self) -> Tuple[Input, Output]:
        raise NotImplementedError("must be implemented in class '%s'" % self.__class__.__name__)

    @property
    def dispatcher_connectors(self) -> Tuple[Input, Output]:
        raise NotImplementedError("must be implemented in class '%s'" % self.__class__.__name__)

    @property
    def requestor_connectors(self) -> Tuple[Input, Output]:
        raise NotImplementedError("must be implemented in class '%s'" % self.__class__.__name__)

    @property
    def assertor_connectors(self) -> Tuple[Input, Output]:
        raise NotImplementedError("must be implemented in class '%s'" % self.__class__.__name__)

    @property
    def reporter_connectors(self) -> Tuple[Input, Output]:
        raise NotImplementedError("must be implemented in class '%s'" % self.__class__.__name__)

    def _start_filter(self):
        inp, out = self.filter_connectors
        Filter(self._ctx.new_filter_context(), inp, out, filters_config=self._cfg.filters).start()

    def _start_transformer(self):
        inp, out = self.transformer_connectors
        Transformer(self._ctx.new_transformer_context(), inp, out, bubbles_config=self._cfg.bubbles).start()

    def _start_dispatcher(self):
        inp, out = self.dispatcher_connectors
        Dispatcher(self._ctx.new_service_context(), inp, out).start()

    def _start_requestor(self):
        inp, out = self.requestor_connectors
        Requestor(self._ctx.new_requestor_context(), inp, out).start()

    def _start_assertor(self):
        inp, out = self.assertor_connectors
        Assertor(self._ctx.new_service_context(), inp, out).start()

    def _start_reporter(self):
        inp, out = self.reporter_connectors
        Reporter(self._ctx.new_reporter_context(), inp, out, report_config=self._cfg.report).start()

    def _run_async(self, target, *args):
        p = self._async_class(target=target, args=args)
        p.daemon = True
        p.start()
        self._processes.append(p)

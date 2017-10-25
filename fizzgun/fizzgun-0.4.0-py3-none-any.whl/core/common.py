from fizzgun.application.service_contexts import ServiceContext


class Input(object):
    def pull(self):
        raise NotImplementedError("'pull' must be implemented in class '%s'" % self.__class__.__name__)


class Output(object):
    def push(self, _result):
        raise NotImplementedError("'push' must be implemented in class '%s'" % self.__class__.__name__)


class ControlMessage(object):
    STOP = 'STOP'


class Worker(object):
    """
    A generic Worker implementation. Receives a work unit and produces a result (or not)
    """
    NO_RESULT = []

    def __init__(self, service_context: ServiceContext, input_src, output, *args, **kwargs):
        self._service_context = service_context
        self._input = input_src
        self._output = output
        self._running = False
        self.initialize(*args, **kwargs)

    def initialize(self, *_args, **_kwargs):
        """Overriden by subclasses to for specific initialization"""
        pass

    def start(self):
        self._running = True
        while self._running:
            work = self._input.pull()
            if self.control(work):
                continue

            for result in self.process(work):
                if self._output:
                    self._output.push(result)

    def control(self, message):
        if message == ControlMessage.STOP:
            self.stop()
            return True
        return False

    def stop(self):
        self._running = False

    @property
    def service_context(self) -> ServiceContext:
        return self._service_context

    def process(self, work):
        """A results generator. Receives a work unit and produces 0 or more results"""
        raise NotImplementedError("'process' must be implemented in class '%s'" % self.__class__.__name__)

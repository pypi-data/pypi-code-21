from fizzgun.application.service_contexts import CmdRunFizzgunContext
from fizzgun.config import Config


class FizzgunRunner(object):

    def __init__(self, context: CmdRunFizzgunContext, config: Config):
        self._ctx = context
        self._cfg = config

    def run(self):
        produce_to = self._start_stack()

        self._start_request_source_provider(produce_to)

    def _start_stack(self):

        queue_type = self._cfg.stack.get('queue_type', 'zmq')

        if queue_type == 'zmq':
            from fizzgun.impl.zmq_flow import ZMQDeployment
            deployment = ZMQDeployment(self._ctx, self._cfg)

        elif queue_type == 'python':
            from fizzgun.impl.queue_flow import QueueDeployment
            deployment = QueueDeployment(self._ctx, self._cfg)

        else:
            raise RuntimeError("Unsupported stack queue_type '%s'" % queue_type)

        return deployment.start()

    def _start_request_source_provider(self, produce_to):
        provider = self._cfg['source']

        if provider == 'mitmproxy':
            from fizzgun.impl.mitm_plugin import MitmPlugin

            mitm = MitmPlugin(self._cfg)
            mitm.start(produce_to)
        else:
            raise RuntimeError("Unsupported provider '%s'" % provider)

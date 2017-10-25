import zmq

from fizzgun.core.deployment import FizzgunDeployment
from fizzgun.core.common import Input, Output


class ZMQConnector(object):
    def __init__(self, address, bind=False):
        self._ctx = zmq.Context()
        self._socket = self._address(address, self._mode(), bind)

    def _mode(self):
        raise NotImplementedError("'_mode' must be implemented in class '%s'" % self.__class__.__name__)

    def _address(self, spec: None or str or int or tuple, mode, bind):
        if not spec:
            return None
        if isinstance(spec, int) or (isinstance(spec, str) and spec.isdigit()):
            address = "tcp://127.0.0.1:%s" % spec
        elif isinstance(spec, tuple) and len(spec) == 2:
            address = "tcp://%s:%d" % spec
        else:
            raise ValueError("ZMQ address should be either a port number or a host+port tuple")
        zmq_socket = self._ctx.socket(mode)
        if bind:
            zmq_socket.bind(address)
        else:
            zmq_socket.connect(address)
        return zmq_socket


class ZMQInput(Input, ZMQConnector):
    def pull(self):
        if not self._socket:
            raise RuntimeError("This connector does not have any input end")
        return self._socket.recv_json()

    def _mode(self):
        return zmq.PULL


class ZMQOutput(Output, ZMQConnector):
    def push(self, result):
        if not self._socket:
            raise RuntimeError("This connector does not have any output end")
        self._socket.send_json(result)

    def _mode(self):
        return zmq.PUSH


class ZMQDeployment(FizzgunDeployment):
    """Runs a full stack of nodes connected by ZMQ queues"""

    def __init__(self, context, config):
        super(ZMQDeployment, self).__init__(context, config, requires_dispatcher=True)
        self._producer_output = ZMQOutput(5550, bind=True)

    @property
    def producer_output(self):
        return self._producer_output

    @property
    def filter_connectors(self):
        return ZMQInput(5550), ZMQOutput(5551, bind=True)

    @property
    def transformer_connectors(self):
        return ZMQInput(5551), ZMQOutput(5552)

    @property
    def dispatcher_connectors(self):
        return ZMQInput(5552, bind=True), ZMQOutput(5553, bind=True)

    @property
    def requestor_connectors(self):
        return ZMQInput(5553), ZMQOutput(5554)

    @property
    def assertor_connectors(self):
        return ZMQInput(5554, bind=True), ZMQOutput(5555, bind=True)

    @property
    def reporter_connectors(self):
        return ZMQInput(5555), None

import zmq

from zmq.asyncio import Context

from oshino import Agent


class ZmqAgent(Agent):

    @property
    def bind(self):
        return self._data.get("bind", None)

    @property
    def connect(self):
        return self._data["connect"]

    async def process(self, event_fn):
        logger = self.get_logger()
        if self.socket_active:
            try:
                logger.trace("Trying to read msg")
                json_obj = await self.socket.recv_json(zmq.NOBLOCK)
                logger.trace("Received msg: '{0}'".format(json_obj))
                event_fn(service=self.prefix, **json_obj)
            except zmq.error.Again:
                logger.trace("No message received")
            except Exception as ex:
                logger.exception(ex)
        else:
            logger.debug("Zmq socket is still waiting for connection")

    def on_start(self):
        logger = self.get_logger()
        logger.info("Initializing zMQ context")
        self.ctx = Context()
        self.socket = self.ctx.socket(zmq.PULL)
        if self.bind:
            self.socket.bind(self.bind)
            logger.info("Zmq socket bound on: {0}".format(self.bind))
            self.socket_active = True
        else:
            self.socket.connect(self.connect)
            logger.info("Zmq socket connected to: {0}".format(self.connect))
            self.socket_active = True

    def on_stop(self):
        self.socket.close()

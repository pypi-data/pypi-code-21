"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.brew.base import Brew
from pubkeeper.brew.websocket.patron import WebsocketPatron
from pubkeeper.brew.websocket.protocols.protocols import get_supported_protocols
from pubkeeper.utils.logging import get_logger
from pubkeeper.brew.websocket import WebsocketSettings
from pubkeeper.utils.websocket import WebsocketConnection
from pubkeeper.brew.websocket.protocols.legacy.protocol import \
    Protocol as DefaultProtocol


class WebsocketBrew(Brew):
    def __init__(self, *args, **kwargs):
        self.logger = get_logger(self.__class__.__name__)
        self.name = 'websocket'
        self._patrons = {}
        self._socket = None
        self._connection = None
        self._connected = False
        self._supported_protocols = get_supported_protocols()
        # set legacy protocol as default
        self._protocol = None

        super().__init__(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        return WebsocketSettings

    def configure(self, context):
        non_casting_types = [type(None), str]
        for setting in WebsocketSettings.keys():
            if context and setting in context:
                _type = type(WebsocketSettings[setting])
                if _type in non_casting_types:
                    WebsocketSettings[setting] = context[setting]
                else:
                    # cast incoming value to known type
                    WebsocketSettings[setting] = _type(context[setting])

    def start(self):
        self.logger.info("Starting websocket brew")

        if self._socket is None:
            self.logger.info("Websocket Brewer Socket Created")
            protocols = ['pubkeeper-{}'.format(p)
                         for p in self._supported_protocols.keys()]

            self._socket = WebsocketConnection({
                'host': WebsocketSettings['ws_host'],
                'port': WebsocketSettings['ws_port'],
                'resource': '',
                'secure': WebsocketSettings['ws_secure'],
                'headers': protocols
            })
            self._socket.start(
                on_message=None,
                on_connected=self.on_connected,
                on_disconnect=self.on_disconnected,
                on_selected_subprotocol=self.on_selected_subprotocol)

    def on_connected(self, connection):
        self._connected = True
        self._connection = connection
        if not self._protocol:
            self._protocol = DefaultProtocol()
        # update protocol for all patrons
        for patron in self._patrons.values():
            patron['patron'].protocol = self._protocol
        # start any non started patrons
        for patron in self._patrons.values():
            if not patron['patron'].started:
                patron['patron'].start()

    def on_disconnected(self):
        self._connected = False
        # stop patrons
        for patron in self._patrons.values():
            patron['patron'].stop()
        self._protocol = None

    def on_selected_subprotocol(self, subprotocol):
        if subprotocol is None:
            return
        self.logger.info('Using brew subprotocol: {}'.format(subprotocol))

        from importlib import import_module
        subprotocol = subprotocol[subprotocol.index('-') + 1:]
        protocol_module = \
            import_module("{}.protocol".
                          format(self._supported_protocols[subprotocol]))
        self._protocol = protocol_module.Protocol()

    def stop(self):
        self.logger.info("Stopping websocket brew")
        if self._socket:
            self._socket.stop()

        for patron in self._patrons.values():
            patron['patron'].stop()

        self._patrons = {}

    def create_brewer(self, brewer):
        self.logger.info('Creating brewer for: {}, {}'.
                         format(brewer.topic, brewer.brewer_id))
        return {
            'hostname': WebsocketSettings['ws_host'],
            'port': WebsocketSettings['ws_port'],
            'secure': WebsocketSettings['ws_secure']
        }

    def start_brewer(self, brewer_id, topic, patron_id, patron):
        self.logger.debug('Starting brewer for: {}, {}.{}'.
                          format(topic, brewer_id, patron_id))
        self._protocol.on_connected(self._connection, topic)

    def stop_brewer(self, brewer_id, topic, patron_id):
        self.logger.debug('Stopping brewer for: {}, {}.{}'.
                          format(topic, brewer_id, patron_id))
        self._protocol.on_disconnected(self._connection, topic)

    def start_patron(self, patron_id, topic, brewer_id, brewer_config,
                     brewer_brew, callback):
        self.logger.debug('Starting patron for: {}, {}.{}'.
                          format(topic, brewer_id, patron_id))
        if topic in self._patrons:
            self.logger.info(
                "Already an existing thread for {} using".format(
                    topic
                )
            )
            self._patrons[topic]['count'] += 1
        else:
            self._patrons[topic] = {
                'count': 1,
                'patron': WebsocketPatron(
                    topic,
                    brewer_brew,
                    callback,
                    self._protocol
                )
            }
            if self._connected:
                self._patrons[topic]['patron'].start()


    def stop_patron(self, patron_id, topic, brewer_id):
        if topic in self._patrons:
            self.logger.debug('Stopping patron for: {}, {}.{}'.
                              format(topic, brewer_id, patron_id))
            self._patrons[topic]['count'] -= 1
            if self._patrons[topic]['count'] <= 0:
                self._patrons[topic]['patron'].stop()
                del(self._patrons[topic])

    def brew(self, brewer_id, topic, data, patrons):
        if self._connected:
            self._protocol.brew(self._connection, brewer_id, topic, data)

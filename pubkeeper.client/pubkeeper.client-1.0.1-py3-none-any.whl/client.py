"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
import pubkeeper.protocol
from pubkeeper.brew.brew_state import BrewState
from pubkeeper.utils.logging import get_logger
from pubkeeper.utils.websocket import WebsocketConnection
from tornado import ioloop
from threading import Thread, RLock, Event
from pkgutil import iter_modules
from importlib import import_module


def client_ready(func):
    def wrapper(self, *args, **kwargs):
        if not self._client_ready.is_set():
            raise RuntimeError("Client is not ready")
        else:
            return func(self, *args, **kwargs)

    return wrapper


class PubkeeperClient(object):
    def __init__(self, jwt, config):
        super().__init__()
        self.logger = get_logger('pubkeeper.client')

        self._jwt = jwt

        # Client known data
        self._client_lock = RLock()

        self._brews = []

        self._client_ready = Event()

        # IOLoop for Client Thread
        self._ioloop = ioloop.IOLoop()

        self.protocol = None

        self._established_protocol = None
        self._supported_protocols = {}
        self._load_protocol_modules()

        versions = ['pubkeeper-{}'.format(p) for
                    p in self._supported_protocols.keys() if
                    p != 'pubkeeper.n.io']

        # Since this version does not adhere to the above scheme, we
        # ignore it there, and just append for now.  Remove when we drop
        # support for legacy
        versions.append('pubkeeper.n.io')

        config['headers'] = versions
        self._connection_module = WebsocketConnection(config)

    def _load_protocol_modules(self):
        for _, modname, _ in iter_modules(
            path=pubkeeper.protocol.__path__,
            prefix=pubkeeper.protocol.__name__ + '.'
        ):
            try:
                module = import_module(modname + ".handler")
            except ImportError:
                self.logger.exception(
                    "Unknown pubkeeper.protocol version {}".format(modname)
                )
                return

            self._supported_protocols[module.protocol_version] = module

    # Client Execution
    def start(self, bridge_mode=False):
        # Start the Client Thread
        self._thread = Thread(target=self.run)
        self._thread.start()

        if not self._client_ready.wait(2):
            raise RuntimeError("Client not ready")

        for brew in self._brews:
            self._ioloop.add_callback(brew.start)

        self.protocol.register_brews([b.name for b in self._brews], bridge_mode)

    def run(self):
        self.logger.info("Pubkeeper Client Running")
        self._ioloop.make_current()
        self._connection_module.start(
            on_connected=self._on_connected,
            on_message=self._on_message,
            on_selected_subprotocol=self._on_selected_subprotocol
        )
        self._ioloop.start()
        self._ioloop.close()
        self.logger.info("Pubkeeper Client Shutdown")

    def _wait_for_callbacks(self, deadline):
        def stop_loop():
            now = self._ioloop.time()
            if now < deadline and self._ioloop._callbacks:
                self._ioloop.add_timeout(now + 0.1, stop_loop)
            else:
                self.close(False)
                self._ioloop.stop()

        stop_loop()

    def shutdown(self):
        self.logger.info("Pubkeeper Client Shutting Down")

        if self.protocol:
            self.protocol.shutdown()

        with self._client_lock:
            for brew in self._brews:
                self._ioloop.add_callback(brew.stop)

        deadline = 10
        self._ioloop.add_callback(self._wait_for_callbacks, deadline)
        self._thread.join(deadline)

    # Connection Handlers
    def _on_connected(self, connection):
        self.logger.info(
            "Connected To Pubkeeper ({0})".format(self._established_protocol)
        )

        self.protocol._connection = connection
        self.protocol.on_connected(self._jwt, 2)

    def _on_message(self, msg):
        self.protocol.on_message(msg)

    def _on_selected_subprotocol(self, selected_subprotocol_str):
        if selected_subprotocol_str == 'pubkeeper.n.io':
            selected_subprotocol = 'pubkeeper.n.io'
            self.protocol_module = import_module(
                "pubkeeper.protocol.legacy.handler"
            )
        else:
            selected_subprotocol = \
                selected_subprotocol_str[selected_subprotocol_str.index('-')+1:]  # noqa
            self.protocol_module = \
                self._supported_protocols[selected_subprotocol]

        if self._established_protocol is None:
            self._established_protocol = selected_subprotocol
            self.protocol = \
                self.protocol_module.ClientProtocolHandler(
                    client_ready=self._client_ready
                )
            self.protocol._brews = self._brews
        else:
            if self._established_protocol != selected_subprotocol:
                self.logger.error(
                    "Unable to upgrade protocol version at runtime"
                )
                self.close()
                return

    def close(self, restart=True):
        self._connection_module.stop(restart)
        self._client_ready.set()

        if not restart:
            self._client_ready.clear()

    # Client API
    def add_brew(self, brew):
        with self._client_lock:
            if [b for b in self._brews if b.name == brew.name]:
                raise RuntimeError("Attempting to add an existing brew")

            # brew.brew_state_listener = self.brew_state
            self._brews.append(brew)

    def remove_brew(self, brew):
        with self._client_lock:
            if brew not in self._brews:
                raise RuntimeError("Attempting to remove a brew "
                                   "that was not added")

            self._brews.remove(brew)

    @client_ready
    def add_brewer(self, topic):
        return self.protocol.add_brewer(topic, self._brews)

    @client_ready
    def remove_brewer(self, brewer):
        self.protocol.remove_brewer(brewer)

    @client_ready
    def add_patron(self, topic, **kwargs):
        return self.protocol.add_patron(topic, self._brews, **kwargs)

    @client_ready
    def remove_patron(self, patron):
        self.protocol.remove_patron(patron)

    @client_ready
    def brew_state(self, brew, state):
        with self._client_lock:
            if not isinstance(state, BrewState):
                raise ValueError("Invalid Brew State specified")

            self.protocol.set_brew_state(brew, state)

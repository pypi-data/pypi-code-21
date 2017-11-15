"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.brew.base import Brew
from pubkeeper.gateway.base import PubkeeperGateway
from pubkeeper.client.protocol import ClientProtocol
from pubkeeper.protocol.packet import ClientAuthenticatePacket, \
    BrewerRegisterPacket, BrewerUnregisterPacket, PatronRegisterPacket, \
    PatronUnregisterPacket, BrewsRegisterPacket, BrewsStatePacket
from pubkeeper.protocol.brew_state import BrewState
from pubkeeper.segment.manager import SegmentManager
from pubkeeper.utils.logging import get_logger
from pubkeeper.utils.exceptions import UnauthenticatedException
from tornado import ioloop, gen
from threading import Thread, RLock


class PubkeeperClient(ClientProtocol):
    def __init__(self, jwt, server_comm, gateway_servers=None,
                 authenticate_timeout=2, **kwargs):
        self.logger = get_logger('pubkeeper.client')
        super().__init__(**kwargs)
        self._jwt = jwt

        self.server_comm = server_comm
        if gateway_servers is not None:
            if not isinstance(gateway_servers, list):
                self.gateway_servers = [gateway_servers]
            else:
                self.gateway_servers = gateway_servers
        else:
            self.gateway_servers = []

        self.gateways = []

        self._data_lock = RLock()

        # Our clients set of brews
        self.brews = []
        self._brews_started = False

        self._authenticate_timeout = authenticate_timeout

        # list of brews supported by client
        self._registered_brews = None
        # keep track of current brew states in case a reconnection occurs
        self._brew_states = {}
        self._bridge_mode = False

        self._ioloop = ioloop.IOLoop()
        self._thread = Thread(target=self.run)
        self._thread.start()

    @property
    def brewers(self):  # pragma: no cover
        return self._brewers

    @property
    def patrons(self):  # pragma: no cover
        return self._patrons

    def run(self):
        self.logger.info("Pubkeeper Client Running")
        self._ioloop.make_current()

        self.server_comm.start(on_message=self.on_message,
                               on_connected=self.on_connected,
                               on_disconnected=self.on_disconnected)

        # Gateway Starts
        for gateway_server in self.gateway_servers:
            gateway = PubkeeperGateway(self, gateway_server)
            gateway.start()
            self.gateways.append(gateway)

        self._ioloop.start()
        self._ioloop.close()
        self.logger.info("Pubkeeper Client Shutdown")

    @gen.coroutine
    def on_connected(self):
        # make sure when there is a new connection to server that
        # segments are removed if any
        SegmentManager.reset()
        try:
            self.server_comm.write_message(
                ClientAuthenticatePacket(token=self._jwt)
            )

            yield self._authenticated_event.wait(
                timeout=self._ioloop.time() + self._authenticate_timeout
            )

            if not self._authenticated:
                raise UnauthenticatedException()

            self.logger.info("Authenticated to Pubkeeper")

            with self._data_lock:
                if self._registered_brews:
                    self._register_brews(self._registered_brews,
                                         self._bridge_mode)

                self._update_brew_states()

                for brewer in self._brewers:
                    self._ioloop.add_callback(self._add_brewer, brewer)

                for patron in self._patrons:
                    self._ioloop.add_callback(self._add_patron, patron)
        except:
            self.logger.error("Could not authenticate")
            self.server_comm.shutdown()

    def on_disconnected(self):  # pragma: no cover
        self._authenticated = False
        self._authenticated_event.clear()

    def shutdown(self):
        self.logger.info("Pubkeeper Client Shutting Down")

        for gateway in self.gateways:
            self.logger.info("Shutting down Gateways")
            self._ioloop.add_callback(gateway.shutdown)

        with self._data_lock:
            for brewer in self._brewers:
                self.remove_brewer(brewer)

            for patron in self._patrons:
                self.remove_patron(patron)

            for brew in self.brews:
                brew.stop()

        self._ioloop.add_callback(self.server_comm.shutdown)
        self._ioloop.stop()

        self._thread.join(5)

    def register_brews(self, brews, bridge_mode):
        # keep track of registered brews in case we are not currently
        # connected or a reconnection occurs
        with self._data_lock:
            self._registered_brews = brews
            self._bridge_mode = bridge_mode

            if self._authenticated:
                self._register_brews(brews, bridge_mode)

    def _register_brews(self, brews, bridge_mode):
        self._ioloop.add_callback(self.server_comm.write_message,
                                  BrewsRegisterPacket(
                                      brews, bridge_mode
                                  ))

    def brew_state(self, brew, state):
        with self._data_lock:
            if not isinstance(state, BrewState):
                raise ValueError("Invalid Brew State specified")

            brew_name = brew.name if isinstance(brew, Brew) else brew
            self._brew_states[brew_name] = state
            if self._authenticated:
                self._ioloop.add_callback(self.server_comm.write_message,
                                          BrewsStatePacket(brew, state)
                                          )

    def _update_brew_states(self):
        for brew, state in self._brew_states.items():
            self._ioloop.add_callback(self.server_comm.write_message,
                                      BrewsStatePacket(brew, state)
                                      )

    def add_brew(self, brew):
        with self._data_lock:
            if [b for b in self.brews if b.name == brew.name]:
                raise RuntimeError("Attempting to add an existing brew")

            brew.brew_state_listener = self.brew_state
            self.brews.append(brew)

    def start_brews(self):
        with self._data_lock:
            for brew in self.brews:
                self._ioloop.add_callback(brew.start)

            self._brews_started = True

    def remove_brew(self, brew):
        with self._data_lock:
            if brew not in self.brews:
                raise RuntimeError("Attempting to remove a brew "
                                   "that was not added")

            self.brews.remove(brew)

    def add_brewer(self, brewer):
        if not self._brews_started:
            raise RuntimeError("Can not add new brewers until brews started")

        with self._data_lock:
            if brewer in self._brewers:
                raise RuntimeError("Brewer already registered with Client")

            self._brewers.append(brewer)
            brewer.brews = self.brews

            if self._authenticated:
                self._ioloop.add_callback(self._add_brewer, brewer)

    def _add_brewer(self, brewer):
        brew_configs = []
        brewer_config = brewer.get_config()

        with self._data_lock:
            for brew in brewer.brews:
                details = {}
                details['name'] = brew.name
                brew_details = brew.create_brewer(brewer)
                if brew_details:
                    if not isinstance(brew_details, dict):
                        self._brewers.remove(brewer)
                        brew.destroy_brewer(brewer)
                        raise RuntimeError("Create Brewer returned a non dict")

                    details.update(brew_details)

                brew_configs.append(details)

        self.server_comm.write_message(BrewerRegisterPacket(
            brewer.topic,
            brewer.brewer_id,
            brewer_config,
            brew_configs
        ))

    def remove_brewer(self, brewer):
        with self._data_lock:
            try:
                self._brewers.remove(brewer)
            except ValueError:
                self.logger.exception("Could not remove brewer from list")
                return

            self._ioloop.add_callback(self._remove_brewer, brewer)

    def _remove_brewer(self, brewer):
        with self._data_lock:
            for brew in self.brews:
                brew.destroy_brewer(brewer)

        self.server_comm.write_message(BrewerUnregisterPacket(
            brewer.topic,
            brewer.brewer_id
        ))

    def add_patron(self, patron, brew_override=None):
        if not self._brews_started:
            raise RuntimeError("Can not add new patrons until brews started")

        with self._data_lock:
            if patron in self._patrons:
                raise RuntimeError("Patron already registered with Client")

            if brew_override is not None:
                for pbrew in brew_override:
                    if pbrew in self.brews:
                        patron.brews.append(pbrew)
                    else:
                        raise RuntimeError(
                            "Override brew ({}) not registered "
                            "with Client".format(pbrew.name)
                        )
            else:
                patron.brews = self.brews

            self._patrons.append(patron)

        if self._authenticated:
            self._ioloop.add_callback(self._add_patron, patron)

    def _add_patron(self, patron):
        brew_configs = []

        with self._data_lock:
            for brew in patron.brews:
                details = {}
                details['name'] = brew.name
                brew_details = brew.create_patron(patron)
                if brew_details:
                    if not isinstance(brew_details, dict):
                        self._patrons.remove(patron)
                        brew.destroy_patron(patron)
                        raise RuntimeError("Create Patron returned a non dict")

                    details.update(brew_details)

                brew_configs.append(details)

        self.server_comm.write_message(PatronRegisterPacket(
            patron.topic,
            patron.patron_id,
            brew_configs
        ))

    def remove_patron(self, patron):
        with self._data_lock:
            try:
                self._patrons.remove(patron)
            except ValueError:
                self.logger.exception("Could not remove brewer from list")
                return

            self._ioloop.add_callback(self._remove_patron, patron)

    def _remove_patron(self, patron):
        with self._data_lock:
            for brew in self.brews:
                brew.destroy_patron(patron)

        self.server_comm.write_message(PatronUnregisterPacket(
            patron.topic,
            patron.patron_id
        ))

    def write_message(self, msg):
        """ write_message

        Wrapper for protocol error packets
        """
        self.server_comm.write_message(msg)

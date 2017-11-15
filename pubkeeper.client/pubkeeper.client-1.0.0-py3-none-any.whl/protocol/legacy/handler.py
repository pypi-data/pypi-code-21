"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.brew.base import Brew
from pubkeeper.protocol.legacy.brewer.brewer import ProtocolBrewer
from pubkeeper.protocol.legacy.patron.patron import ProtocolPatron
from pubkeeper.protocol.legacy.protocol import PubkeeperProtocol
from pubkeeper.protocol.legacy.packet import *  # noqa
from pubkeeper.protocol.legacy import protocol_version  # noqa
from pubkeeper.protocol.legacy.segment.manager import SegmentManager
from tornado import gen, ioloop
from tornado.locks import Event
from threading import RLock


class ClientProtocolHandler(PubkeeperProtocol):
    def __init__(self, *args, state_change_callback=None,
                 client_ready=None, **kwargs):
        super().__init__(*args, **kwargs)

        self._authenticated = False
        self._authenticated_event = Event()
        self._state_change_callback = state_change_callback
        self._client_ready = client_ready

        self._ioloop = ioloop.IOLoop.current()

        self._data_lock = RLock()
        self._registered_brews = None
        self._bridge_mode = False

        self._brewers = []
        self._patrons = []

        self._connection = None

        self._brews_state = {}

        self.handlers.update({
            Packet.CLIENT_AUTHENTICATED: self.on_client_authenticated,
            Packet.BREWER_NOTIFY: self.on_brewer_notify,
            Packet.BREWER_REMOVED: self.on_brewer_removed,
            Packet.PATRON_NOTIFY: self.on_patron_notify,
            Packet.PATRON_REMOVED: self.on_patron_removed,
            Packet.SEGMENT_CREATE: self.on_segment_create,
            Packet.SEGMENT_DESTROY: self.on_segment_destroy,
            Packet.SEGMENT_CONNECT_BREWER: self.on_segment_connect_brewer,
        })

    def on_disconnected(self):
        if self._client_ready:
            self._client_ready.clear()

    def write_message(self, msg):
        if self._connection:
            self._connection.write_message(msg)

    @gen.coroutine
    def on_connected(self, jwt, authenticate_timeout):
        try:
            self._write_message(
                ClientAuthenticatePacket(token=jwt)
            )

            yield self._authenticated_event.wait(
                timeout=self._ioloop.time() + authenticate_timeout
            )

            if not self._authenticated:
                raise RuntimeError()

            self.logger.info("Authenticated to Pubkeeper")
        except:
            self.logger.warn("Could not authenticate")
            return

        if self._registered_brews:
            self._ioloop.add_callback(self._write_message,
                                      BrewsRegisterPacket(
                                          self._registered_brews,
                                          self._bridge_mode
                                      ))

        self._update_brews_state()

        for brewer in self._brewers:
            self._ioloop.add_callback(self._add_brewer, brewer)

        for patron in self._patrons:
            self._ioloop.add_callback(self._add_patron, patron)

        if self._client_ready:
            self._client_ready.set()

    def shutdown(self):
        with self._data_lock:
            for brewer in self._brewers:
                self.remove_brewer(brewer)

            for patron in self._patrons:
                self.remove_patron(patron)

    # Protocol Handlers
    def on_client_authenticated(self, authenticated):
        if authenticated:
            self._authenticated = True
            self._authenticated_event.set()
        else:
            self._authenticated = False
            self._authenticated_event.clear()

    def on_brewer_notify(self, patron_id, brewers):
        with self._data_lock:
            for patron in [p for p in self._patrons
                           if p.patron_id == patron_id]:
                patron.new_brewers(brewers)

                if self._state_change_callback:
                    self._state_change_callback(Packet.BREWER_NOTIFY,
                                                patron)

    def on_brewer_removed(self, topic, patron_id, brewer_id):
        with self._data_lock:
            for patron in [p for p in self._patrons
                           if p.patron_id == patron_id]:
                patron.remove_brewer(brewer_id)

                if self._state_change_callback:
                    self._state_change_callback(Packet.BREWER_REMOVED,
                                                patron)

    def on_patron_notify(self, brewer_id, patrons):
        with self._data_lock:
            for brewer in [b for b in self._brewers
                           if b.brewer_id == brewer_id]:
                brewer.new_patrons(patrons)

                if self._state_change_callback:
                    self._state_change_callback(Packet.PATRON_NOTIFY,
                                                brewer)

    def on_patron_removed(self, topic, brewer_id, patron_id):
        with self._data_lock:
            for brewer in [b for b in self._brewers
                           if b.brewer_id == brewer_id]:
                brewer.remove_patron(patron_id)

                if self._state_change_callback:
                    self._state_change_callback(Packet.PATRON_REMOVED,
                                                brewer)

    def on_segment_create(self, segment_id, topic,
                          brewer_details, patron_details):
        with self._data_lock:
            new_brewer_brew, new_patron_brew = \
                SegmentManager.create(self, segment_id, topic,
                                      brewer_details, patron_details)

            self._write_message(SegmentRegisterPacket(
                segment_id,
                new_brewer_brew,
                new_patron_brew
            ))

    def on_segment_connect_brewer(self, segment_id, patron_id, patron_brew):
        with self._data_lock:
            SegmentManager.connect_brewer(segment_id, patron_id, patron_brew)

    def on_segment_destroy(self, segment_id):
        with self._data_lock:
            SegmentManager.destroy(segment_id)

    # Protocol Implementations
    def register_brews(self, brews, bridge_mode):
        with self._data_lock:
            self._registered_brews = brews
            self._bridge_mode = bridge_mode

            self._ioloop.add_callback(self._write_message,
                                      BrewsRegisterPacket(
                                          brews, bridge_mode
                                      ))

    def set_brew_state(self, brew, state):
        brew_name = brew.name if isinstance(brew, Brew) else brew
        self._brews_state[brew_name] = state

        if self._authenticated:
            self._ioloop.add_callback(self._write_message,
                                      BrewsStatePacket(brew_name, state))

    def _update_brews_state(self):
        for brew_name, state in self._brews_state.items():
            self._ioloop.add_callback(self._write_message,
                                      BrewsStatePacket(brew_name, state))

    def add_brewer(self, topic, brews):
        brewer = ProtocolBrewer(topic)

        with self._data_lock:
            self._brewers.append(brewer)
            brewer.brews = brews

            if self._authenticated:
                self._ioloop.add_callback(self._add_brewer, brewer)

        return brewer

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

        self._write_message(BrewerRegisterPacket(
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
            for brew in brewer.brews:
                brew.destroy_brewer(brewer)

        self._write_message(BrewerUnregisterPacket(
            brewer.topic,
            brewer.brewer_id
        ))

    def add_patron(self, topic, brews, brew_override=None, **kwargs):
        patron = ProtocolPatron(topic, **kwargs)

        with self._data_lock:
            if brew_override is not None:
                for pbrew in brew_override:
                    if pbrew in brews:
                        patron.brews.append(pbrew)
                    else:
                        raise RuntimeError(
                            "Override brew ({}) not registered "
                            "with Client".format(pbrew.name)
                        )
            else:
                patron.brews = brews

            self._patrons.append(patron)

        if self._authenticated:
            self._ioloop.add_callback(self._add_patron, patron)

        return patron

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

        self._write_message(PatronRegisterPacket(
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
            for brew in patron.brews:
                brew.destroy_patron(patron)

        self._write_message(PatronUnregisterPacket(
            patron.topic,
            patron.patron_id
        ))

"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.protocol import PubkeeperClientProtocol
from pubkeeper.protocol.packet import Packet, SegmentRegisterPacket
from pubkeeper.segment.manager import SegmentManager
from tornado.locks import Event


class ClientProtocol(PubkeeperClientProtocol):
    def __init__(self, state_change_callback=None):
        super().__init__()
        self._authenticated = False
        self._authenticated_event = Event()
        self._state_change_callback = state_change_callback

        # Our brewers and patrons
        self._brewers = []
        self._patrons = []

    def on_client_authenticated(self, authenticated):
        with self._data_lock:
            if authenticated:
                self._authenticated = True
                self._authenticated_event.set()

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
            # send to server brewer and patron details to connect to
            # original patron and brewer respectively
            self._ioloop.add_callback(
                self.server_comm.write_message,
                SegmentRegisterPacket(segment_id,
                                      new_brewer_brew,
                                      new_patron_brew)
            )

    def on_segment_connect_brewer(self, segment_id, patron_id, patron_brew):
        with self._data_lock:
            SegmentManager.connect_brewer(segment_id, patron_id, patron_brew)

    def on_segment_destroy(self, segment_id):
        with self._data_lock:
            SegmentManager.destroy(segment_id)

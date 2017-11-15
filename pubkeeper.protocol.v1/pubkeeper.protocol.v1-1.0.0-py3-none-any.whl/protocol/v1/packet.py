"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from enum import IntEnum
from struct import pack
import json


class Packet(IntEnum):
    """Packet Constants"""
    # Auth
    CLIENT_AUTHENTICATE = 1   # Client -> Server
    CLIENT_AUTHENTICATED = 2  # Server -> Client

    # Brewer
    BREWER_REGISTER = 10      # Brewer -> Server
    BREWER_UNREGISTER = 11    # Brewer -> Server
    BREWER_NOTIFY = 12        # Server -> Patron
    BREWER_REMOVED = 13       # Server -> Patron

    # Patron
    PATRON_REGISTER = 20      # Patron -> Server
    PATRON_UNREGISTER = 21    # Patron -> Server
    PATRON_NOTIFY = 22        # Server -> Brewer
    PATRON_REMOVED = 23       # Server -> Brewer

    # Bridge-Segment
    SEGMENT_CREATE = 30          # Server -> Client
    SEGMENT_DESTROY = 31         # Server -> Client
    SEGMENT_REGISTER = 32        # Client -> Server
    SEGMENT_CONNECT_BREWER = 33  # Server -> Client

    # Brews
    BREWS_REGISTER = 40       # Client -> Server
    BREW_STATE = 41       # Client -> Server

    # Errors
    ERROR = 99


class PubkeeperPacket(object):
    _packet_format = '<HH4x'

    def gen_packet(self):
        """Generate json string from values
        """
        payload = json.dumps(self.payload).encode()

        return pack('{}{}s'.format(self._packet_format, len(payload)),
                    self.packet.value, len(payload), payload)


class ClientAuthenticatePacket(PubkeeperPacket):
    def __init__(self, token):
        """Client Authenticate Packet

        Send a packet authenticating to the server

        Args:
            token (string) - Issued JWT
        """
        if token is None:
            raise ValueError("ClientAuthenticate: Need to Provide a token")

        self.packet = Packet.CLIENT_AUTHENTICATE
        self.payload = {
            'token': token
        }


class ClientAuthenticatedPacket(PubkeeperPacket):
    def __init__(self, authenticated):
        """Client Authenticated Packet

        Packet issued from server to client depicting authenticated state

        Args:
            authenticated (bool) - Authenticated state
        """
        if authenticated is None:
            raise ValueError("ClientAuthenticated: Need to Provide"
                             "authenticated")

        self.packet = Packet.CLIENT_AUTHENTICATED
        self.payload = {
            'authenticated': authenticated
        }


class BrewerRegisterPacket(PubkeeperPacket):
    def __init__(self, topic, brewer_id, brewer_config, brews):
        """Brewer Registration

        Packet to register a brewer

        Args:
            topic (string) - Topic of publication.  This may not be wildcarded.
            brewer_id (uuid) - UUID of Brewer
            brewer_config (dict) - Any configuration that the brewer
                                   has (eg. crypto)
            brews (list) - Set of potential transport for the given brewer
        """
        if topic is None or brewer_id is None or \
                brewer_config is None or brews is None:
            raise ValueError("BrewerRegister: Need to Provide a topic, "
                             "brewer_id, brewer_config, and brews")

        self.packet = Packet.BREWER_REGISTER
        self.payload = {
            'topic': topic,
            'brewer_id': brewer_id,
            'brewer_config': brewer_config,
            'brews': brews
        }


class BrewerUnregisterPacket(PubkeeperPacket):
    def __init__(self, topic, brewer_id):
        """Brewer Unregistration

        Packet to unregister a brewer

        Args:
            topic (string) - Topic used for registeration of brewer
            brewer_id (uuid) - UUID of Brewer
        """
        if topic is None or brewer_id is None:
            raise ValueError("BrewerUnregister: Need to Provide a topic, "
                             "and brewer_id")

        self.packet = Packet.BREWER_UNREGISTER
        self.payload = {
            'topic': topic,
            'brewer_id': brewer_id
        }


class BrewerNotifyPacket(PubkeeperPacket):
    def __init__(self, patron_id, brewers):
        """New Brewer Notification

        Packet alerting clients of new brewers in the system

        Args:
            patron_id (uuid) - UUID of the clients patron subscribing
            brewers (list) - List of brewers.  On initial patron registration
                this will contain a list of all of the brewers of the given
                topic.  Subsiquently, as new brewers join the network, the
                list will contain a single element of the new brewer.  The
                contents of the list will be a dictionary containing a:
                    topic (string) - Topic of publication
                    brewer_id (uuid) - UUID of the network brewer brewing
                    brewer_config (dict) - Any configuration that the brewer
                                           has (eg. crypto)
                    brew (dict) - Brew configuration options
        """
        if patron_id is None or brewers is None:
            raise ValueError("BrewerNotify: Need to Provide a "
                             "patron_id, and brewers")

        self.packet = Packet.BREWER_NOTIFY
        self.payload = {
            'patron_id': patron_id,
            'brewers': brewers
        }


class BrewerRemovedPacket(PubkeeperPacket):
    def __init__(self, topic, patron_id, brewer_id):
        """Removed Brewer Notification

        Packet alerting clients of brewers removed from the system

        Args:
            topic (string) - Topic of publication
            patron_id (uuid) - UUID of the clients patron subscribing
            brewer_id (uuid) - UUID of the network brewer brewing
        """
        if topic is None or patron_id is None or brewer_id is None:
            raise ValueError("BrewerRemoved: Need to Provide a topic, "
                             "patron_id, and brewer_id")

        self.packet = Packet.BREWER_REMOVED
        self.payload = {
            'topic': topic,
            'patron_id': patron_id,
            'brewer_id': brewer_id
        }


class PatronRegisterPacket(PubkeeperPacket):
    def __init__(self, topic, patron_id, brews):
        """Patron Registration

        Packet to register a patron

        Args:
            topic (string) - Topic of subscription.  This may be wildcarded.
            patron_id (uuid) - UUID of Patron
            brews (list) - Set of potential transport for the given patron
        """
        if topic is None or patron_id is None or brews is None:
            raise ValueError("PatronRegister: Need to Provide a topic, "
                             "patron_id, and brews")

        self.packet = Packet.PATRON_REGISTER
        self.payload = {
            'topic': topic,
            'patron_id': patron_id,
            'brews': brews
        }


class PatronUnregisterPacket(PubkeeperPacket):
    def __init__(self, topic, patron_id):
        """Patron Registration

        Packet to unregister a patron

        Args:
            topic (string) - Topic used for patron subscription
            patron_id (uuid) - UUID of Patron
        """
        if topic is None or patron_id is None:
            raise ValueError("PatronUnregister: Need to Provide a topic, "
                             "and patron_id")

        self.packet = Packet.PATRON_UNREGISTER
        self.payload = {
            'topic': topic,
            'patron_id': patron_id
        }


class PatronNotifyPacket(PubkeeperPacket):
    def __init__(self, brewer_id, patrons):
        """New Patron Notification

        Packet alerting clients of new patrons in the system

        Args:
            brewer_id (uuid) - UUID of the clients brewer brewing
            patrons (list) - List of patrons.  On initial patron registration
                this will contain a list of all of the patrons of the given
                topic.  Subsiquently, as new patrons join the network, the
                list will contain a single element of the new patrons.  The
                contents of the list will be a dictionary containing a:
                    topic (string) - Topic of publication
                    patron_id (uuid) - UUID of the network patron brewing
                    brew (dict) - Brew configuration options
        """
        if brewer_id is None or patrons is None:
            raise ValueError("PatronNotify: Need to Provide a "
                             "brewer_id, and patrons")

        self.packet = Packet.PATRON_NOTIFY
        self.payload = {
            'brewer_id': brewer_id,
            'patrons': patrons
        }


class PatronRemovedPacket(PubkeeperPacket):
    def __init__(self, topic, brewer_id, patron_id):
        """Removed Patron Notification

        Packet alerting clients of patrons removed from the system

        Args:
            topic (string) - Topic of subscription
            brewer_id (uuid) - UUID of the clients brewer brewing
            patron_id (uuid) - UUID of the network patron subscribing
        """
        if topic is None or patron_id is None:
            raise ValueError("PatronRemoved: Need to Provide a topic, "
                             "brewer_id, and patron_id")

        self.packet = Packet.PATRON_REMOVED
        self.payload = {
            'topic': topic,
            'brewer_id': brewer_id,
            'patron_id': patron_id
        }


class ErrorPacket(PubkeeperPacket):
    def __init__(self, message):
        """Report an error

        Args:
            message (string) - Error message
        """
        if message is None:
            raise ValueError("Error: Need to Provide a topic, and patron")

        self.packet = Packet.ERROR
        self.payload = {
            'message': message
        }


class BrewsRegisterPacket(PubkeeperPacket):
    def __init__(self, brews, bridge_mode):
        """Brews Registration Notification

        Args:
            brews (list): list of brew names
            bridge_mode (bool) - Specifies if client can be part of a bridge
        """
        self.packet = Packet.BREWS_REGISTER
        self.payload = {
            'brews': brews,
            'bridge_mode': bridge_mode
        }


class BrewsStatePacket(PubkeeperPacket):
    def __init__(self, brew, state):
        """Brew State Notification

        Args:
            brew: brew name
            state (BrewState) - Specifies brew state
        """
        self.packet = Packet.BREW_STATE
        self.payload = {
            'brew': brew,
            'state': state
        }


class SegmentCreatePacket(PubkeeperPacket):
    def __init__(self,
                 segment_id,
                 patron_details,
                 brewer_details):
        """Segment Create Packet Notification

        Packet alerting client that a segment needs to be created

        Args:
            segment_id (uuid) - segment UUID
            patron_details (dict) - contains settings used to create
                tmp_patron which patronizes previous brewer.
                    patron_id: created temp patron id
                    brewer_id: brewer_id to patronize
                    topic: topic for brewer_id to patronize
                    brew details: brew to patronize
            brewer_details (dict) - contains settings used to create
                tmp_brew which receives from tmp_patron created and
                brews to next patron in bridge.
                    brewer_id: created temp brewer id
                    brew_name: temp brew name to brew on
                    topic: temp topic to brew on
        """
        self.packet = Packet.SEGMENT_CREATE
        self.payload = {
            'segment_id': segment_id,
            'patron_details': patron_details,
            'brewer_details': brewer_details
        }


class SegmentRegisterPacket(PubkeeperPacket):
    def __init__(self, segment_id, brewer_brew, patron_brew):
        """Segment Register Packet Notification

        Packet alerting server of segment construct details.
        Server will match brewer_details with segment original patron needs
        Server will match patron_details with segment original brewer needs

        Args:
            segment_id (uuid) - segment UUID
            brewer_brew (dict) - brewer brew created by segment
            patron_brew (dict) - patron brew created by segment
        """
        self.packet = Packet.SEGMENT_REGISTER
        self.payload = {
            'segment_id': segment_id,
            'brewer_brew': brewer_brew,
            'patron_brew': patron_brew
        }


class SegmentConnectBrewer(PubkeeperPacket):
    def __init__(self, segment_id, patron_id, patron_brew):
        """Segment Connect Brewer Packet Notification

        Packet alerting server to associate a brewer with a patron brew.

        Args:
            segment_id (uuid) - segment UUID
            patron_id (uuid) - patron UUID
            patron_brew (dict) - patron brew
        """
        self.packet = Packet.SEGMENT_CONNECT_BREWER
        self.payload = {
            'segment_id': segment_id,
            'patron_id': patron_id,
            'patron_brew': patron_brew
        }


class SegmentDestroyPacket(PubkeeperPacket):
    def __init__(self, segment_id):
        """Segment Destroy Packet Notification

        Packet alerting client that segment is to be destroyed

        Args:
            segment_id (uuid) - segment UUID
        """
        self.packet = Packet.SEGMENT_DESTROY
        self.payload = {
            'segment_id': segment_id
        }

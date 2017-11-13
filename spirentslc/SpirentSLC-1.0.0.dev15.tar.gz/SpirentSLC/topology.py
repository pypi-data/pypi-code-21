# ****************       BEGIN-STANDARD-COPYRIGHT      ***************
#
# Copyright (c) 2017, Spirent Communications.
#
# All rights reserved. Proprietary and confidential information of Spirent Communications.
#
#  ***************        END-STANDARD-COPYRIGHT       ***************

"""Topology class and necessary tools."""

from .session_profile import SessionProfile
from .identity import UriIdentity
from .python_name import python_name



class Topology(UriIdentity):
    """Topology representation.

    Provide a list of devices with sessions
    """

    def __init__(self, project, uri, devices, protocol):
        """Initiates a new topology.

        Arguments:
        protocol_socket -- an instance of ProtocolSocket. It must be connected by the time open() is called.
        agent_type -- agent type (local/itest/velocity)
        uri -- topology URI, e.g. project://my_project/topologies/ServerAndPC.tbml
        devices -- a list of DeviceData objects
        """
        UriIdentity.__init__(self, uri)
        self._project = project
        self._devices = dict((dev.name, Device(self, dev.uri, dev.sessions, protocol)) for dev in devices)

    def agent_type(self):
        """ Agent type"""
        return self._project.agent_type

    def list(self):
        """Return a list of devices available"""
        return list(self._devices.keys())

    def __dir__(self):
        """ return a list of methods available to project"""
        res = super.__dir__(self) + self.list()
        return res

    def __getitem__(self, key):
        """ Return a device by name"""
        return self._devices.get(key)

    def __getattr__(self, key):
        """ Return a device by name"""
        ret = self[key]
        if ret == None:
            raise AttributeError(key)
        return ret

class DeviceData(object):
    """ A device details """
    def __init__(self, name, uri, sessions):
        self.name = name
        self.uri = uri
        self.sessions = sessions

class Device(UriIdentity):
    """ A device in topology"""

    def __init__(self, topology, name, sessions, protocol):
        """ Initialize a device reference handle contained in topology """
        UriIdentity.__init__(self, topology.uri + '#' + name)
        self._topology = topology
        self._name = name
        self._protocol = protocol
        self._sessions = dict((python_name(session), self._create_session(session)) for session in sessions)

    def _create_session(self, session):
        session_uri =  self.uri + ':' + session
        return SessionProfile(self._protocol, self.agent_type(), session_uri)

    def agent_type(self):
        """ A type of agent"""
        return self._topology.agent_type()

    def name(self):
        """ A name of device """
        return self._name

    def list(self):
        """ A list of available sessions"""
        return list(self._sessions.keys())

    def __dir__(self):
        """ return a list of methods available to project"""
        res = super.__dir__(self) + self.list()
        return res

    def __getitem__(self, key):
        """ Return a device session by name"""
        return self._sessions.get(key)

    def __getattr__(self, key):
        """ Return a device session by name"""
        ret = self[key]
        if ret is None:
            raise AttributeError(key)
        return ret

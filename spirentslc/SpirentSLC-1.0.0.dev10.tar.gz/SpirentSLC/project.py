# ****************       BEGIN-STANDARD-COPYRIGHT      ***************
#
# Copyright (c) 2017, Spirent Communications.
#
# All rights reserved. Proprietary and confidential information of Spirent Communications.
#
#  ***************        END-STANDARD-COPYRIGHT       ***************

"""Project class and necessary tools."""

import re
import six
from .session_profile import SessionProfile
from .topology import Topology, DeviceData
from .resources import ParameterFile, ResponseMapFile
from .identity import UriIdentity

from .python_name import python_name

if six.PY2:
    from urllib import quote
else:
    from urllib.parse import quote

class Project(UriIdentity):
    """This class represents a single project.

    Objects of this class should not be created directly, but rather obtained from an SLC object.
    """

    def __init__(self, project_name, protocol_socket, agent_type):
        UriIdentity.__init__(self, 'project://%s/' % str(project_name))
        self.project_name = project_name
        self._protosock = protocol_socket
        self.agent_type = agent_type

        self._update_agent_type()

        self._session_profiles = dict()
        self._topologies = dict()
        self._parameter_files = dict()
        self._response_maps = dict()

    def __str__(self):
        """Return a project name"""
        return self.project_name

    def open(self):
        """
        Parses itar and init a list of all the usable topologies and session profiles in the project.

        Returns self for convenience.
        """

        self._update_project_list()

        return self

    def _resource_name(self, itest_name, suffix):
        pos_from = itest_name.rfind('/') + 1
        pos_to = itest_name.rfind('.')
        return self._python_name(itest_name[pos_from:pos_to] + suffix)

    def _python_name(self, name):
       return python_name(name)

    def _update_agent_type(self):
        """ Detect agent type based on init packet send by server """
        pass

    def _update_project_list(self):
        ret = self._protosock.query_project(self.project_name, parameter_file=True, response_map=True)

        def _as_list(value, new_value):
            if value == None:
                value = new_value
            elif type(value) == list:
                value.append(new_value)
            else:
                value = [value, new_value]
            return value

        def _find(value, uri):
            if value != None:
                if isinstance(value, list):
                    for resource in value:
                        if resource.uri == uri:
                            return True
                else:
                    # value instanceof SessionProfile, Topology, ParameterFile or ResponseMapFile
                    if value.uri == uri:
                        return True

            return False

        def _check_prefix(value):
            if value.startswith('/'):
                return value[1:]
            return value

        for session_profile in ret.sessionProfiles:
            name = self._resource_name(session_profile, '_ffsp')
            uri = 'project://%s/%s' %(quote(self.project_name), quote(_check_prefix(session_profile)))

            value = self._session_profiles.get(name)

            # Check existance
            if _find(value, uri):
                continue
            # Update new value
            new_value = SessionProfile(self._protosock, self.agent_type, uri)
            self._session_profiles[name] = _as_list(value, new_value)

        for topology in ret.topologies:
            name = self._resource_name(topology.name, '_tbml')
            topology_uri = 'project://%s/%s' %(quote(self.project_name), quote(_check_prefix(topology.name)))

            value = self._topologies.get(name)
            if _find(value, topology_uri):
                continue

            devices = [DeviceData(self._python_name(device.name), quote(device.name), device.sessions) for device in topology.devices]
            new_value = Topology(self, topology_uri, devices, self._protosock)

            self._topologies[name] = _as_list(value, new_value)

        for param_file in ret.parameterFiles:
            name = self._resource_name(param_file, '_ffpt')
            uri = 'project://%s/%s' %(quote(self.project_name), quote(_check_prefix(param_file)))

            value = self._parameter_files.get(name)
            if _find(value, uri):
                continue
            new_value = ParameterFile(uri)
            self._parameter_files[name] = _as_list(value, new_value)

        for response_file in ret.responseMaps:
            name = self._resource_name(response_file, '_ffrm')
            uri = 'project://%s/%s' %(quote(self.project_name), quote(_check_prefix(response_file)))

            value = self._response_maps.get(name)
            if _find(value, uri):
                continue

            new_value = ResponseMapFile(uri)
            self._response_maps[name] = _as_list(value, new_value)

    def list(self, session_file=True, parameter_file=False, response_map=False, topology_file=True):
        """
        Returns a list of names of all the usable topologies and session profiles in the project.

        Resources with duplicate names will be shown once,
        but all access methods will return a list of resources with same name.

        Filter parameters:
        session_file -- include session files
        parameter_file -- include parameter files
        response_map -- include response map files
        topology_file -- include topology files

        Example:
            proj.list()
            ==> ['dut1_ffsp', 'lab1_setup_tbml']
        """
        self._update_project_list()

        result = list()
        if session_file:
            result += list(self._session_profiles.keys())

        if topology_file:
            result += list(self._topologies.keys())

        if parameter_file:
            result += list(self._parameter_files.keys())

        if response_map:
            result += list(self._response_maps.keys())

        return result

    def __dir__(self):
        """ return a list of methods available to project"""
        res = super.__dir__(self) + self.list(session_file=True, parameter_file=True, response_map=True, topology_file=True)
        return res

    def response_maps(self):
        """
        Returns a list of reseponse maps.

        Example:
            proj.response_maps()
            ==> ['dut1_ffrm', 'lab1_setup_ffrm']
        """
        return self.list(response_map=True, session_file=False, topology_file=False)

    def parameter_files(self):
        """
        Returns a list of parameter files

        Example:
            proj.response_maps()
            ==> ['dut1_ffrm', 'lab1_setup_ffrm']
        """
        return self.list(parameter_file=True, session_file=False, topology_file=False)

    def __getitem__(self, key):
        """
            Sessions are opened either directly on a session profile or local topology.

            Examples:
                s1 = proj.dut1_ffsp.open()
                s1 = proj.rest_session_ffsp.open(url='https://my_site.my_domain.com', accept_all_cookies=True)
                s1 = proj.rest_session_ffsp.open(parameter_file=proj.main_setup_ffpt)
                s1 = proj.rest_session_ffsp.open(
                    properties={'authentication.authentication': 'Basic', 'authentication.user': 'me', 'authentication.password': 'totes_secret!'})

            Opening native sessions:
                s1 = slc.sessions.ssh.open(ip_address='10.20.30.40')
        """
        profile = self._session_profiles.get(key)
        if profile:
            return profile

        topology = self._topologies.get(key)
        if topology:
            return topology

        parameter = self._parameter_files.get(key)
        if parameter:
            return parameter

        response_map = self._response_maps.get(key)
        if response_map:
            return response_map

        return None

    def __getattr__(self, key):
        ret = self[key]
        if ret is None:
            raise AttributeError(key)
        return ret

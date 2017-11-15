# ****************       BEGIN-STANDARD-COPYRIGHT      ***************
#
# Copyright (c) 2017, Spirent Communications.
#
# All rights reserved. Proprietary and confidential information of Spirent Communications.
#
#  ***************        END-STANDARD-COPYRIGHT       ***************

"""Session profile class and necessary tools."""

import six

from .internal.protocol import Type

from .session_response import SessionActionResponse
from .resources import ParameterFile, ResponseMapFile
from .identity import UriIdentity

_KNOWN_INVOKE_ARGS = ['response_map', 'parameters', 'command', 'properties']

def _to_invoke_args(kwargs):
    """Prepares the given arguments dict for invoking as action arguments.

    Arguments:
    kwargs -- dict or arguments

    Returns a new dict, ready to be passed as arguments to invoke_command().
    """

    ret = {}
    params = {}

    for key, value in kwargs.items():
        if key in _KNOWN_INVOKE_ARGS:
            ret[key] = value
        else:
            params[key] = value

    if params:
        ret['parameters'] = params
    return ret

def _to_list(arg):
    """If arg is a list, returns it. If it's None, returns None. Otherwise, returns a one-element list with arg."""

    if arg is None:
        return None

    if isinstance(arg, list):
        return arg

    return [arg,]

def _to_requirements(agent_requirements):
    """Converts the given argument into a list of Type.Requirement.

    Arguments:
    agent_requirements -- dict of the format {'requirement_name': 'requirement_value'}. Can be None.

    Returns a list of Type.Requirement, or None.
    """

    if not agent_requirements:
        return None

    ret = []
    for key, value in agent_requirements.items():
        req = Type.Requirement()
        req.name = key
        req.value = value
        ret.append(req)

    return ret

def _to_property_group(properties):
    """Converts the given properties dict into Type.PropertiesGroup.

    Arguments:
        properties -- a dictionary with keys being property names (strings)
                      and value being property values (strings or nested properties group).
                      Can be None.

    Returns Type.PropertiesGroup, or None.
    """

    if not properties:
        return None

    ret = Type.PropertiesGroup()
    ret.name = ''

    for key, value in properties.items():
        if isinstance(value, six.string_types):
            # prop = Type.Property()
            prop = ret.properties.add()
            prop.name = key
            prop.value = value
        elif isinstance(value, list):
            for item in value:
                child = _to_property_group(item)
                child.name = key
                ret.children.extend([child])
        else:
            child = _to_property_group(value)
            if child:
                child.name = key
                ret.children.extend([child])

    return ret

def _to_params_list(parameters):
    """Converts the given parameters to a list of Type.Param.

    Arguments:
    parameters -- a dict with keys being parameter names and values being either parameter values, or
                  a dict with two keys: 'value', which is the parameter value, and 'children', which is a dict
                  of the same type as above. Example:
                  {'param1': 'value1', 'param2': {'value': 'value2', 'children': {'child_param1': 'value3'}}}
                  Can be None.

    Returns a list of Type.Param, or None.
    """

    if not parameters:
        return None

    ret = []

    for key, value in parameters.items():
        param = Type.Param()
        param.name = key
        if isinstance(value, ParameterFile):
            param.value = value.uri
        elif isinstance(value, ResponseMapFile):
            param.value = value.uri
        elif isinstance(value, dict):
            param.value = str(value['value'])
            if 'children' in value:
                param.parameters.extend(_to_params_list(value['children']))
        else:
            param.value = str(value)

        ret.append(param)

    return ret

class SessionProfileInformation(object):
    """ A details object to specify agent parameters"""

    def __init__(self, agent_name, agent_id, protocol_version, agent_type, capabilities ):
        """Initialise a agent parameters object
        agent_name -- a name of agent.
        agent_id -- a identifier of agent.
        protocol_version -- a version of protocol used
        """
        self.name = agent_id
        self.agent_name = agent_name
        self.protocol_version = protocol_version
        self.agent_type = agent_type
        self.capabilities = {}

        for cap in capabilities:
            cur_cap = self.capabilities.get(cap.name)
            if cur_cap is None:
                cur_cap = cap.value
            elif type(cur_cap) == list:
                cur_cap.append(cap.value)
            else:
                cur_cap = [cur_cap, cap.value]
            self.capabilities[cap.name] = cur_cap

    def __str__(self):
        return str(vars(self))

class SessionProfile(UriIdentity):
    """Session profile representation.

    Allows to open and close session, as well as invoking its actions and quickcalls.

    Recommended way to use this class is as follows:

        with proj.session_name_ffsp.open() as s1:
            # invoke a quickcall:
            response = s1.init_routes(all=True)

            # invoke a command:
            response = s1.command('command', response_map=proj.response_map_ffrm)

    Constructing instances of this class directly may be handy for testing, but generally is discouraged.

    Properties:
    agent -- agent information
    session_id -- if the session is opened, this will be a string representation of the session's ID.
                  Otherwise, this will be None. May be used to check is the session is opened.
    """

    def __init__(self, protocol_socket, agent_type, uri, dependencies=None):
        """Initiates a new session profile.

        Arguments:
        protocol_socket -- an instance of ProtocolSocket. It must be connected by the time open() is called.
        uri -- session profile URI, e.g. project://my_project/session_profiles/slc_test.ffsp
        dependencies -- session profile dependencies,
                        e.g. ['file:///home/dsavenko/itest/itest/dev/src/non-plugins/SpirentSLC/my_project.itar']

        """

        UriIdentity.__init__(self, uri)
        self._protosock = protocol_socket
        self._deps = dependencies

        self.agent = SessionProfileInformation(self._protosock.agent_name, self._protosock.agent_id, self._protosock.protocol_version, agent_type, self._protosock.capabilities)
        self.session_id = None
        self._quickcalls = None
        self.open_response = None

    def open(self, parameter_file=None, agent_requirements=None, properties=None, response_map_lib=None, **kwargs):
        """Opens the session.

        Arguments:
        parameter_file -- a single parameter file (URI), or a list of parameter files.
        agent_requirements -- dict of the format {'requirement_name': 'requirement_value'}
        properties -- a dictionary with keys being property names (strings)
                      and value being property values (strings or nested properties group).

        Raises ValueError, if the session is already opened. May raise socket.error.
        """

        if self.session_id:
            raise ValueError('Session already opened with id=' + self.session_id)

        if properties is None:
            properties = {}
            for key, value in kwargs.items():
                properties[key] = str(value)

        # Convert parameter file to uri
        if isinstance(parameter_file, ParameterFile):
            parameter_file = parameter_file.uri

        # Convert project to uri
        if isinstance(response_map_lib, UriIdentity):
            response_map_lib = response_map_lib.uri

        if response_map_lib != None and not (type(response_map_lib) in six.string_types):
            raise ValueError('Wrong response_map_lib value is passed. Should be URI' + str(response_map_lib))


        rsp = self._protosock.start_session(self._uri,
                                            dependencies=self._deps,
                                            param_files=_to_list(parameter_file),
                                            requirements=_to_requirements(agent_requirements),
                                            property_group=_to_property_group(properties),
                                            resp_map_lib=response_map_lib)
        self.session_id = rsp.sessionId
        self.open_response = SessionActionResponse(rsp)
        return self

    def close(self):
        """Closes the session.

        Does nothing, if the session has not been opened yet. May raise socket.error.
        """

        session_id = self.session_id
        self.session_id = None
        self.open_response = None
        if session_id:
            self._protosock.close_session(session_id)

    def is_open(self):
        """ Return if session is stil opened or not"""
        return self.session_id != None and self._protosock != None and self._protosock.is_open()

    def session_properties(self):
        """Query a running session for all session properties"""
        return self.invoke_action('session_properties')

    def step_properties(self, action, command=None, parameters=None, properties=None, response_map=None):
        """Query a running session for step actin properties"""
        return self.invoke_action('step_properties_' + action, command=command, parameters=parameters, properties=properties, response_map=response_map )

    def invoke_action(self, action, command=None, parameters=None, response_map=None, properties=None):
        """Invokes session action or quickcall.

        Generally, you do not need to use this method directly. E.g. instead of calling

            ssh_session.invoke_action('command', 'ls')

        you can just call

            ssh_session.command('ls')

        For Quickcalls, instead of calling

            session.invoke_action('my_quickcall', parameters={'param1': 'value1', 'param2': 123})

        you can just call

            session.my_quickcall(param1='value1', param2=123)

        Arguments:
        action -- session action or QuickCall name. Depends on a session.
                  Widely used actions: 'close' to close the session, 'command' to execute a specific session command.
        command -- command to execute
        parameters -- a dict with keys being parameter names and values being either parameter values, or
                      a dict with two keys: 'value', which is the parameter value, and 'children', which is a dict
                      of the same type as above. Example:
                      {'param1': 'value1', 'param2': {'value': 'value2', 'children': {'child_param1': 'value3'}}}
        properties -- a dictionary with keys being property names (strings)
                      and value being property values (strings or nested properties group).
                      A {'param_group.param': 'value1'} syntax could be used to update nested values.
        responseMap -- URI of the response map file to use.

        Returns action response. Console calling is equivalent to response._text.
        Raises ValueError, if the session is not opened. May raise socket.error
        """

        if not self.session_id:
            raise ValueError('Session is not opened')

        # Convert response map to it uri
        if isinstance(response_map, ResponseMapFile):
            response_map = response_map.uri

        resp = self._protosock.invoke_action(self.session_id,
                                             action=action,
                                             command=str(command),
                                             params=_to_params_list(parameters),
                                             response_map=response_map,
                                             property_group=_to_property_group(properties))
        #if (isinstance(resp, InvokeResponse)):
        #    return resp.reportResult, resp.error
        #else:
        #    return SessionActionResponse(resp)
        return SessionActionResponse(resp)

    def list(self, qc_name=None):
        """Returns all QuickCalls available on a given session profile"""

        if qc_name:
            resp = self._protosock.query_session(self._uri, qc_name)
            qc = resp.quickCall[0]
            return dict((arg.name, arg.description) for arg in qc.args)

        if not self._quickcalls:
            self._quickcalls = dict()
            resp = self._protosock.query_session(self._uri)
            for qc in resp.quickCall:
                self._quickcalls[qc.name] = dict((arg.name, arg.description) for arg in qc.args)

        return self._quickcalls

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __dir__(self):
        """ return a list of methods available to project"""
        res = super.__dir__(self) + list(self.list().keys())
        return res
    def __getitem__(self, key):
        return lambda *args, **kwargs: self.invoke_action(key, *args, **_to_invoke_args(kwargs))

    def __getattr__(self, key):
        ret = self[key]
        if not ret:
            raise AttributeError(key)
        return ret

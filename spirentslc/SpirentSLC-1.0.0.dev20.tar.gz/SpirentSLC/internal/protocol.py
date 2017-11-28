# ****************       BEGIN-STANDARD-COPYRIGHT      ***************
#
# Copyright (c) 2017, Spirent Communications.
#
# All rights reserved. Proprietary and confidential information of Spirent Communications.
#
#  ***************        END-STANDARD-COPYRIGHT       ***************

"""Protocol implementation.

ProtocolSocket class provides low-level implementation of the Protobuf-based protocol communicating with agents.
"""

import uuid
import time
import socket
import six
import os

# pylint: disable=no-name-in-module,import-error
from google.protobuf.internal import encoder

from . import ExecutionProtocol_pb2 as pb

if six.PY3:
    # pylint: disable=redefined-builtin,invalid-name
    long = int

_PROTOCOL_LOGGING = 'True' == os.getenv('SLC_DEBUG_PROTOCOL', 'False')

_EXECUTION_MESSAGE_SUBTYPE_INFO = {
    # pylint: disable=bad-whitespace

    # This map is used to wrap messages into ExecutionMessage. The keys are messages classes, and values are
    # pairs (message type, message field name) in ExecutionMessage.
    # It's safer not to use it directly, but use _get_msg_subtype_info() instead.

    # EXECUTION MESSAGES:

    pb.CancelMessage:           (pb.ExecutionMessage.CANCEL_MESSAGE,            'cancelMessage'),
    pb.HeartbeatMessage:        (pb.ExecutionMessage.HEARTBEAT_MESSAGE,         'heartbeatMessage'),
    pb.InitMessage:             (pb.ExecutionMessage.INIT_MESSAGE,              'initMessage'),
    pb.InvokeAck:               (pb.ExecutionMessage.INVOKE_ACK,                'invokeAck'),
    pb.InvokeMessage:           (pb.ExecutionMessage.INVOKE_MESSAGE,            'invokeMessage'),
    pb.InvokeResponse:          (pb.ExecutionMessage.INVOKE_RESPONSE,           'invokeResponse'),
    pb.ReportMessage:           (pb.ExecutionMessage.REPORT_MESSAGE,            'reportMessage'),
    pb.StepMessage:             (pb.ExecutionMessage.STEP_MESSAGE,              'stepMessage'),
    pb.TerminateMessage:        (pb.ExecutionMessage.TERMINATE_MESSAGE,         'terminateMessage'),
    pb.TokenMessage:            (pb.ExecutionMessage.TOKEN_MESSAGE,             'tokenMessage'),
    pb.ExecutionIssueMessage:   (pb.ExecutionMessage.EXECUTION_ISSUE_MESSAGE,   'executionIssueMessage'),

    # SESSION CONTROL MESSAGES:

    pb.NewSession:                  (pb.ExecutionMessage.NEW_SESSION_MESSAGE,           'newSessionMessage'),
    pb.NewSessionResponse:          (pb.ExecutionMessage.NEW_SESSION_RESPONSE,          'newSessionResponse'),
    pb.SendTerminalData:            (pb.ExecutionMessage.SEND_TERMINAL_DATA_MESSAGE,    'sendTerminalDataMessage'),
    pb.SendTerminalDataResponse:    (pb.ExecutionMessage.SEND_TERMINAL_DATA_RESPONSE,   'sendTerminalDataResponse'),
    pb.SessionAction:               (pb.ExecutionMessage.SESSION_ACTION_MESSAGE,        'sessionActionMessage'),
    pb.SessionActionResponse:       (pb.ExecutionMessage.SESSION_ACTION_RESPONSE,       'sessionActionResponse'),
    pb.ListProjects:                (pb.ExecutionMessage.LIST_PROJECTS,                 'listProjects'),
    pb.ListProjectsResponse:        (pb.ExecutionMessage.LIST_PROJECTS_RESPONSE,        'listProjectsResponse'),
    pb.QueryProject:                (pb.ExecutionMessage.QUERY_PROJECT,                 'queryProject'),
    pb.QueryProjectResponse:        (pb.ExecutionMessage.QUERY_PROJECT_RESPONSE,        'queryProjectResponse'),
    pb.QuerySession:                (pb.ExecutionMessage.QUERY_SESSION,                 'querySession'),
    pb.QuerySessionResponse:        (pb.ExecutionMessage.QUERY_SESSION_RESPONSE,        'querySessionResponse')
}

class ProtocolError(socket.error):
    """Any protocol-related error."""
    pass

def _get_msg_subtype_info(klass):
    if klass not in _EXECUTION_MESSAGE_SUBTYPE_INFO:
        raise ValueError('Unrecognized message class ' + str(klass))

    return _EXECUTION_MESSAGE_SUBTYPE_INFO[klass]

def _recv_bytes(sock, length):
    """Receives the given number of bytes from socket.

    Arguments:
    sock -- socket to receive from.
    length -- number of bytes to receive.

    Returns the bytes as a byte string. Blocks until the given number of bytes is read. Raises socket.error, if
    the socket is closed prematurely.
    """

    chunks = []
    bytes_recd = 0
    while bytes_recd < length:
        chunk = sock.recv(min(length - bytes_recd, 8192))
        if chunk == b'':
            raise socket.error("Socket connection broken")
        chunks.append(chunk)
        bytes_recd = bytes_recd + len(chunk)
    return b''.join(chunks)

def _send_bytes(sock, msg):
    """Sends the given message (string) to the socket.

    Arguments:
    sock -- socket to send to.
    msg -- string to send.

    Blocks until the message is sent fully. Raises socket.error, if the socket is closed prematurely.
    """

    length = len(msg)
    total = 0
    while total < length:
        sent = sock.send(msg[total:])
        if sent == 0:
            raise socket.error("Socket connection broken")
        total = total + sent

def _read_varint(sock):
    """Reads varint from socket.

    Originally taken from google.protobuf.internal.decoder._VarintDecoder and modified for reading varints from sockets.

    Arguments:
    sock -- socket to read from.

    Returns pair (value, bytes_read). Raises ValueError on invalid varint.
    """

    mask = (1 << 64) - 1
    result_type = long

    result = 0
    shift = 0
    pos = 0
    # pylint: disable=superfluous-parens,invalid-name,bad-option-value,redefined-variable-type
    while 1:
        b = six.indexbytes(_recv_bytes(sock, 1), 0)
        result |= ((b & 0x7f) << shift)
        pos += 1
        if not (b & 0x80):
            result &= mask
            result = result_type(result)
            return (result, pos)
        shift += 7
        if shift >= 64:
            raise ValueError('Too many bytes when decoding varint.')

def _ensure_msg_type(msg, expected_type):
    if msg.type != expected_type:
        raise ProtocolError('Expected to receive ' + msg.Type.Name(expected_type) + ' from agent, but received ' +
                            msg.Type.Name(msg.type))

def _unwrap(msg):
    for k in _EXECUTION_MESSAGE_SUBTYPE_INFO:
        msg_type, msg_field = _EXECUTION_MESSAGE_SUBTYPE_INFO[k]
        if msg_type == msg.type:
            return getattr(msg, msg_field)
    raise ValueError('Unrecognized message type ' + str(msg.type))

def _read_delimited_msg(sock):
    """Reads delimited message from socket.

    Arguments:
    sock -- socket to read from.
    unwrapToKlass -- if not None, tries to unwrap the received message to the given class. See unwrap() for details.
                     Otherwise, return ExecutionMessage.
                     Default: None.

    Returns the message.
    """

    data_len, _ = _read_varint(sock)
    data = _recv_bytes(sock, data_len)
    ret = pb.ExecutionMessage()
    ret.ParseFromString(data)
    return ret

def _wrap(msg):
    """Wraps the given message into ExecutionMessage.

    Arguments:
    msg -- message to wrap.

    Returns ExecutionMessage, which wrapped the given message. If the given message is already an ExecutionMessage,
    just returns the given message.

    Raises ValueError, if the given message is not of a recognized message type.
    """

    if isinstance(msg, pb.ExecutionMessage):
        return msg

    msg_type, msg_field = _get_msg_subtype_info(type(msg))

    ret = pb.ExecutionMessage()
    ret.type = msg_type
    getattr(ret, msg_field).CopyFrom(msg)

    return ret

def _write_delimited_msg(sock, msg):
    """Writes delimited message to the socket.

    Arguments:
    sock -- socket to write to.
    msg -- protobuf message to write. If it's not already wrapped, it will be wrapped first. See wrap().

    May raise socket.error.
    """

    wrapped = _wrap(msg)

    if _PROTOCOL_LOGGING:
        print("_write:", wrapped)

    msg_str = wrapped.SerializeToString()

    # pylint: disable=protected-access
    delim = encoder._VarintBytes(len(msg_str))

    _send_bytes(sock, delim + msg_str)

def _force_connect(host, port, timeout, agent_process):
    """Constantly tries to connect to the given host/port pair for the given timeout in seconds (approximately).

    Arguments:
    host -- hostname or IP
    port -- port number
    timeout -- timeout in seconds

    If connection is successful, returns the connected socket. If the timeout is passed, but connection is not
    established, raises a TimeoutError.
    """

    start_time = time.time()
    attempt_counter = 0
    while time.time() - start_time < timeout:
        try:
            attempt_counter += 1
            return socket.create_connection((host, port))
        except IOError:
            time.sleep(0.1)

        if agent_process != None:
            pp = agent_process.poll()
            if pp != None:
                raise Exception('Velocity agent process is terminated')

        if attempt_counter == 30:
            print('trying to connect to host', host)
            attempt_counter = 0
    err_msg = 'Fail to connect to host %(host)s port:%(port)d in %(timeout)d sec.' %{"host": host, "timeout": timeout, "port": port}
    if six.PY2:
        raise IOError(err_msg)
    else:
        raise TimeoutError(err_msg)


class Type(object):
    """Directly expose some PB classes to the user. It's really the most reasonable way."""

    # pylint: disable=invalid-name
    Param = pb.Param
    Requirement = pb.NewSession.Requirement
    PropertiesGroup = pb.PropertiesGroup
    Property = pb.PropertiesGroup.Property

class ProtocolSocket(object):
    """This class implements Protobuf-based protocol of communication with agents.

    Unless specified otherwise, this class's methods, including the constructor, may raise socket.error and
    ProtocolError (which is a sub-class of socket.error).
    """

    def __init__(self, host, port, timeout=60, agent_process = None):
        """Creates a new protocol socket.

        Arguments:
        host -- hostname (or IP address) to connect to.
        port -- port number.
        timeout -- timeout in seconds.

        It tries to connect to the given host/port pair for the given timeout in seconds (approximately).
        If connection is successful, a new ProtocolSocket is returned. Otherwise, socket.error is raised.
        If connection is successful, but the peer doesn't behave as expected (probably, it's not an agent),
        ProtocolError is raised.

        Do not forget to call close(), when you're done.
        """
        self._sock = None
        self.agent_name = None
        self.agent_id = None
        self.protocol_version = None

        try:
            self._sock = _force_connect(host, port, timeout, agent_process)
            msg = _read_delimited_msg(self._sock)
            _ensure_msg_type(msg, msg.INIT_MESSAGE)
            self.agent_id = msg.initMessage.agentId
            self.agent_name = msg.initMessage.agentName
            self.protocol_version = msg.initMessage.protocolVersion

            #  Store capability
            self.capabilities = msg.initMessage.capability
        except socket.error as err:
            self.close()
            raise

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def is_open(self):
        """ Return true if connection is alive """
        return self._sock != None

    def close(self):
        """Closes the protocol socket."""

        sock = self._sock
        self._sock = None
        if sock:
            try:
                # sock.shutdown(socket.SHUT_RDWR)
                sock.close()
            except socket.error as err:
                print("failed with socket close", err )

    def _read(self, predicate):
        """Reads messages until the given predicate is True.

        Arguments:
        predicate -- a function with one argument (ExecutionMessage) and a boolean return value. If it returns True,
                     this method stops and returns this message. If it returns False, this method reads the next
                     message.

        Returns the messages read on which the predicate is True.
        """

        while True:
            msg = _read_delimited_msg(self._sock)
            if predicate(msg):
                if _PROTOCOL_LOGGING:
                    print("_read:", msg)
                msg = _unwrap(msg)
                return msg

    def _write(self, msg):
        """Writes the given message to socket.

        Arguments:
        msg -- message to write. If it's not an instance of ExecutionMessage, it will be wrapped to ExecutionMessage.
        """
        _write_delimited_msg(self._sock, msg)

    def start_session(self, session_uri, dependencies=None, param_files=None, requirements=None, property_group=None, resp_map_lib=None):
        """Starts a new session.

        Arguments:
        session_uri -- session URI, e.g. 'project://my_project/session_profiles/ssh_session.ffsp'.
        dependencies -- a list of project URIs this session depend on, e.g. ['file:///tmp/ws/my_project.itar'].
        param_files -- a list of parameter file URIs.
        requirements -- a list of Type.Requirement instances.
        property_group -- a Type.PropertyGroup instance.
        resp_map_lib -- URI of Response Map Library. i.e 'project://map_library/'

        Returns a new session response.
        """

        try:
            msg = pb.NewSession()
            msg.sessionId = str(uuid.uuid1())
            msg.sessionUri = session_uri
            if dependencies:
                msg.dependencyUri.extend(dependencies)
            if param_files:
                msg.paramFileUri.extend(param_files)
            if requirements:
                msg.requirement.extend(requirements)
            if property_group:
                msg.properties.CopyFrom(property_group)
            if resp_map_lib:
                msg.responseMapLib = resp_map_lib
            self._write(msg)
            ret = self._read(lambda msg: msg.type == msg.NEW_SESSION_RESPONSE)
            ret.sessionId = msg.sessionId
            return ret
        except socket.error as err:
            self.close()
            raise

    def invoke_action(self, session_id, action, command=None, params=None, response_map=None, property_group=None):
        """Executes a session action or QuickCall and returns the result.

        Arguments:
        session_id -- session ID (string). The session must be started first. See 'start_session()'.
        action -- session action or QuickCall name. Depends on a session.
                  Widely used actions: 'close' to close the session, 'command' to execute a specific session command.
        command -- command to execute
        params -- a list of Type.Param instances.
        properties -- a map of action properties
        responseMap -- URI of the response map file to use.

        Returns session action response.
        """

        if self._sock is None:
            raise IOError("Connection socket closed")

        try:
            msg = pb.SessionAction()
            msg.sessionId = session_id
            msg.action = action
            if command:
                msg.command = command
            if params:
                msg.parameters.extend(params)
            if property_group:
                msg.properties.CopyFrom(property_group)
            if response_map:
                msg.responseMapMode = msg.FILE
                msg.responseMap = response_map
            self._write(msg)
            return self._read(lambda msg: msg.type in [msg.SESSION_ACTION_RESPONSE, msg.INVOKE_RESPONSE])
        except:
            self.close()
            raise

    def close_session(self, session_id):
        """Closes session with the given ID.

        Arguments:
        session_id -- session ID (string). The session must be started first. See 'start_session()'.

        Returns session action response.
        """

        return self.invoke_action(session_id, 'close')

    def invoke_command(self, session_id, command):
        """Executes a session command.

        Arguments:
        session_id -- session ID (string). The session must be started first. See 'start_session()'.
        command -- command to execute.

        Returns session action response.
        """

        return self.invoke_action(session_id, 'command', command=command)

    def list_projects(self):
        """Returns a list of project names that are accessible to the current user (if authenticated through Velocity) within the applicable context.
             - For a local agent it should list all projects that are available within the ITAR_PATH.
             - For a iTest GUI instance it should list all projects in the workspace.
             - For Velocity, it should list all projects available within all repos that the user has access to.

             When working through Velocity the names include the repo path ('/main/') within them.
             When working outside of Velocity only the project name will be returned. I.e. 'my_project'.
        """
        try:
            msg = pb.ListProjects()
            self._write(msg)
            ret = self._read(lambda msg: msg.type == msg.LIST_PROJECTS_RESPONSE)

            return ret.projects
        except:
            self.close()
            raise

    def query_project(self, project, session_profile=True, topology=True, parameter_file=False, response_map=False):
        """Returns all usable resources in project: session profiles, topologies, property files and response maps.

        Arguments:
        project -- name of project (string).
        session_profile -- Include the list of session profiles to result (boolean). Default True.
        topology -- Include the list of topologies to result (boolean). Default True.
        parameter_file -- Include the list of parameter files to result (boolean). Default False.
        response_map -- Include the list of response maps to result (boolean). Default False.
        """

        try:
            msg = pb.QueryProject()
            msg.project = project
            msg.sessionProfiles = session_profile
            msg.topologies = topology
            msg.parameterFiles = parameter_file
            msg.responseMaps = response_map
            self._write(msg)

            return self._read(lambda msg: msg.type == msg.QUERY_PROJECT_RESPONSE)
        except:
            self.close()
            raise

    def query_session(self, session_uri, qc_name=None):
        """Returns all QuickCalls available on a given session

        Arguments:
        session_uri -- session URI (string).
        """

        try:
            msg = pb.QuerySession()
            msg.sessionUri = session_uri

            if qc_name:
                msg.specificQC = qc_name
            self._write(msg)

            return self._read(lambda msg: msg.type == msg.QUERY_SESSION_RESPONSE)
        except:
            self.close()
            raise

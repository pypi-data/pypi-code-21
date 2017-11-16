# coding: utf-8
from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
from builtins import *

import atexit
import logging
import sys
import zmq

from collections import Iterable
from ctypes import *
from enum import Enum
from six import string_types

from . import tecrpc
from .tecrpc.Argument import *
from .tecrpc.ArgumentType import *
from .tecrpc.Header import *
from .tecrpc.Message import *
from .tecrpc.OperationType import *
from .tecrpc.Reply import *
from .tecrpc.Request import *
from .tecrpc.Status import *
import flatbuffers
from flatbuffers import number_types as N

from ..constant import *
from ..exception import *
from .tecutil_rpc import TecUtilRPC, ValueType

from . import patch_flatbuffers


log = logging.getLogger(__name__)


def Int8Array(self, j=None):
    return self._tab.GetVector(30, c_int8, j)


def Uint8Array(self, j=None):
    return self._tab.GetVector(32, c_uint8, j)


def Int16Array(self, j=None):
    return self._tab.GetVector(34, c_int16, j)


def Uint16Array(self, j=None):
    return self._tab.GetVector(36, c_uint16, j)


def Int32Array(self, j=None):
    return self._tab.GetVector(38, c_int32, j)


def Uint32Array(self, j=None):
    return self._tab.GetVector(40, c_uint32, j)


def Int64Array(self, j=None):
    return self._tab.GetVector(42, c_int64, j)


def Uint64Array(self, j=None):
    return self._tab.GetVector(44, c_uint64, j)


def Float32Array(self, j=None):
    return self._tab.GetVector(46, c_float, j)


def Float64Array(self, j=None):
    return self._tab.GetVector(48, c_double, j)

tecrpc.Argument.Argument.Int8Array = Int8Array
tecrpc.Argument.Argument.Uint8Array = Uint8Array
tecrpc.Argument.Argument.Int16Array = Int16Array
tecrpc.Argument.Argument.Uint16Array = Uint16Array
tecrpc.Argument.Argument.Int32Array = Int32Array
tecrpc.Argument.Argument.Uint32Array = Uint32Array
tecrpc.Argument.Argument.Int64Array = Int64Array
tecrpc.Argument.Argument.Uint64Array = Uint64Array
tecrpc.Argument.Argument.Float32Array = Float32Array
tecrpc.Argument.Argument.Float64Array = Float64Array


def build_null_arg(builder):
    ArgumentStart(builder)
    ArgumentAddType(builder, ArgumentType.Null)
    return ArgumentEnd(builder)


def build_scalar_arg(builder, argtype, arg):
    ArgumentStart(builder)
    if argtype is c_bool:
        ArgumentAddBoolean(builder, arg)
    elif argtype is c_int32:
        ArgumentAddInt32Value(builder, arg)
    elif argtype is c_uint32:
        ArgumentAddUint32Value(builder, arg)
    elif argtype is c_int64:
        ArgumentAddInt64Value(builder, arg)
    elif argtype is c_uint64:
        ArgumentAddUint64Value(builder, arg)
    elif argtype is c_float:
        ArgumentAddFloat32Value(builder, arg)
    elif argtype is c_double:
        ArgumentAddFloat64Value(builder, arg)
    else:
        raise TecplotNotImplementedError(argtype, arg)
    return ArgumentEnd(builder)


def build_array_arg(builder, argtype, arg):
    if argtype is None:
        # just send meta info for array
        ArgumentStart(builder)
        _types = {
            c_int32: ArgumentType.Int32,
            c_int64: ArgumentType.Int64,
            c_float: ArgumentType.Float32,
            c_double: ArgumentType.Float64}
        ArgumentAddType(builder, ArgumentType.Array | _types[arg._type_])
        ArgumentAddUint64Value(builder, len(arg))
    else:
        v = builder.CreateVector(argtype, arg)
        ArgumentStart(builder)
        if argtype is c_uint8:
            ArgumentAddUint8Array(builder, v)
        elif argtype is c_uint32:
            ArgumentAddUint32Array(builder, v)
        elif argtype is c_uint64:
            ArgumentAddUint64Array(builder, v)
        elif argtype is c_int32:
            ArgumentAddInt32Array(builder, v)
        elif argtype is c_int64:
            ArgumentAddInt64Array(builder, v)
        elif argtype is c_float:
            ArgumentAddFloat32Array(builder, v)
        elif argtype is c_double:
            ArgumentAddFloat64Array(builder, v)
        else:
            raise TecplotNotImplementedError(argtype, arg, v)
    return ArgumentEnd(builder)


def build_text_arg(builder, arg):
    if isinstance(arg, c_char):
        arg = arg.value.decode('utf-8')
    a = builder.CreateString(arg)
    ArgumentStart(builder)
    ArgumentAddText(builder, a)
    return ArgumentEnd(builder)


def build_arbparam_arg(builder, argtype, arg):
    if isinstance(arg, POINTER(c_char)):
        arg = cast(arg, c_char_p).value.decode('utf-8')
    if isinstance(arg, string_types):
        a = builder.CreateString(arg or '')
        ArgumentStart(builder)
        ArgumentAddType(builder, ArgumentType.Text)
        ArgumentAddText(builder, a)
        return ArgumentEnd(builder)
    else:
        ArgumentStart(builder)
        if argtype is POINTER:
            ArgumentAddType(builder, ArgumentType.Address)
            ArgumentAddUint64Value(builder, arg)
        elif isinstance(arg, Enum):
            ArgumentAddInt64Value(builder, arg.value)
        else:
            i = int(getattr(arg, 'value', arg))
            ArgumentAddInt64Value(builder, c_int64(i).value)
        return ArgumentEnd(builder)


def build_address_arg(builder, argtype, arg):
    assert argtype is c_uint64
    ArgumentStart(builder)
    if arg is None:
        ArgumentAddType(builder, ArgumentType.Null)
    else:
        ArgumentAddUint64Value(builder, arg)
    return ArgumentEnd(builder)


def build_request(builder, tecutil_command, *args, **kwargs):
    lock = kwargs.pop('lock', True)
    opname = builder.CreateString(tecutil_command)

    reqargs = []
    for valtype, argtype, arg in args:
        if arg is None:
            reqargs.append(build_null_arg(builder))
        elif valtype == ValueType.Scalar:
            reqargs.append(build_scalar_arg(builder, argtype, arg))
        elif valtype == ValueType.Array:
            reqargs.append(build_array_arg(builder, argtype, arg))
        elif valtype == ValueType.Text:
            reqargs.append(build_text_arg(builder, arg))
        elif valtype == ValueType.ArbParam:
            reqargs.append(build_arbparam_arg(builder, argtype, arg))
        elif valtype == ValueType.Address:
            reqargs.append(build_address_arg(builder, argtype, arg))
        else:
            raise TecplotNotImplementedError(valtype, argtype, arg)

    RequestStartArgsVector(builder, len(reqargs))
    for arg in reversed(reqargs):
        builder.PrependUOffsetTRelative(arg)
    args = builder.EndVector(len(reqargs))

    RequestStart(builder)
    reqtype = OperationType.TecUtil
    if lock:
        reqtype |= OperationType.LockRequired
    RequestAddType(builder, reqtype)
    RequestAddArgs(builder, args)
    RequestAddOperation(builder, opname)
    request = RequestEnd(builder)

    MessageStart(builder)
    MessageAddRequest(builder, request)
    reqmsg = MessageEnd(builder)

    builder.Finish(reqmsg)


class TecUtilClient(TecUtilRPC):
    def __init__(self):
        self.socket = None

    def connect(self, host='localhost', port=7600, timeout=10, quiet=False):
        # Prepare the ZeroMQ context
        self._context = zmq.Context()

        # Setup the request server socket
        self.socket = self._context.socket(zmq.REQ)

        # Set high water mark for out-going messages.
        # This is the maximum number of messages to
        # store in the out-going queue - send() will
        # block until the HWM is below this limit.
        self.socket.setsockopt(zmq.SNDHWM, 10)

        # Do not linger once socket is closed.
        # Send messages immediately, and possibly
        # fail, but do not attempt to recover.
        self.socket.setsockopt(zmq.LINGER, 0)

        # Connect requester to the reply sever
        self.endpoint = "tcp://{host}:{port}".format(host=host, port=port)
        self.socket.connect(self.endpoint)

        self.wait_for_connection(timeout, quiet)

        if self.connected:
            atexit.register(self.disconnect)

    def wait_for_connection(self, timeout=10, quiet=False):

        def post_message(msg, quiet=quiet):
            if not quiet:
                if log.getEffectiveLevel() <= logging.INFO:
                    log.info(msg)
                else:
                    print(msg)

        post_message(
            'Connecting to Tecplot 360 TecUtil Server on:\n    {}'.format(
                self.endpoint))

        if not self.is_server_listening(timeout):
            self.disconnect()
            raise TecplotTimeoutError('Failed to connect to TecUtil Server.')

        post_message('Connection established.')

    def is_server_listening(self, timeout=10):
        if self.socket is None:
            raise TecplotLogicError('Not connected to Tecplot 360.')

        builder = flatbuffers.Builder(0)
        opname = builder.CreateString('UTHR?')
        RequestStart(builder)
        RequestAddType(builder, OperationType.Server)
        RequestAddOperation(builder, opname)
        request = RequestEnd(builder)
        MessageStart(builder)
        MessageAddRequest(builder, request)
        reqmsg = MessageEnd(builder)
        builder.Finish(reqmsg)

        self.socket.send(builder.Output())

        poller = zmq.Poller()
        poller.register(self.socket, zmq.POLLIN)
        if poller.poll(timeout * 1000):
            msg = self.socket.recv()
            rep = Message.GetRootAsMessage(msg, 0).Reply()
            if rep.Status() == Status.Success:
                return True

        return False

    @property
    def connected(self):
        return self.socket is not None

    def disconnect(self):
        if sys.version_info >= (3,):
            atexit.unregister(self.disconnect)
        if self.socket:
            self.socket.disconnect(self.endpoint)
            self.socket = None

    def sndrcv(self, tecutil_command, *args, **kwargs):
        builder = flatbuffers.Builder(0)
        build_request(builder, tecutil_command, *args, **kwargs)
        self.socket.send(builder.Output())
        reply_message = self.socket.recv()
        return Message.GetRootAsMessage(reply_message, 0)

    def chk(self, reply):
        if reply.Status() != Status.Success:
            errmsg = reply.Log()
            if not isinstance(errmsg, string_types):
                errmsg = errmsg.decode('utf-8')
            raise TecplotSystemError(errmsg)

    def read_arbparam(self, arg):
        T = ArgumentType
        t = arg.Type()
        if t & (T.Unspecified | T.Address):
            return arg.Int64Value()
        elif t & T.Null:
            return None
        elif t & T.Text:
            txt = arg.Text()
            if isinstance(txt, string_types):
                txt = cast(c_char_p(txt), POINTER(c_char))
            else:
                txt = cast(arg.Text(), POINTER(c_char))
            return txt
        else:
            TecplotNotImplementedError

    def read_text(self, arg):
        T = ArgumentType
        t = arg.Type()
        if t & (T.Unspecified | T.Text):
            txt = arg.Text()
            try:
                txt = txt.decode('utf-8')
            except AttributeError:
                pass
            return txt
        elif t & T.Null:
            return None
        else:
            TecplotNotImplementedError

    def read_ptr(self, arg):
        return arg.Uint64Value()

    def read_array(self, arg, argtype):
        _dispatch = {
            c_uint8: arg.Uint8Array,
            c_int8: arg.Int8Array,
        }
        return _dispatch[argtype]()

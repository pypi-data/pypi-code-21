import os
import threading

import time

import sys
import traceback

from whatap.io.data_outputx import DataOutputX

from whatap import logging

import ctypes

from whatap.trace.trace_context_manager import TraceContextManager

_get_dict = ctypes.pythonapi._PyObject_GetDictPtr
_get_dict.restype = ctypes.POINTER(ctypes.py_object)
_get_dict.argtypes = [ctypes.py_object]


def get_dict(obj):
    return _get_dict(obj).contents.value


class PacketEnum(object):
    PACKET_BUFFER_SIZE = 48 * 1024
    PACKET_BUFFER_MAX_SIZE = 64 * 1024
    
    SERVER = "127.0.0.1"
    PORT = 6600
    PACKET_VERSION = 20101
    PACKET_HEADER_SIZE = 9
    
    PACKET_HEADER_TYPE_POS = 0
    PACKET_HEADER_TYPE_SIZE = 1
    
    PACKET_HEADER_VERSION_POS = 1
    PACKET_HEADER_VERSION_SIZE = 4
    
    PACKET_HEADER_LEN_POS = 5
    PACKET_HEADER_LEN_SIZE = 4
    
    PACKET_TEXT_POS = 45
    
    READ_MAX = 1024


class PacketTypeEnum(object):
    PACKET_BLANK = 0
    PACKET_REQUEST = 1
    PACKET_DB_CONN = 2
    PACKET_DB_FETCH = 3
    PACKET_DB_SQL = 4  # DB SQL start ~ end
    PACKET_DB_SQL_START = 5
    PACKET_DB_SQL_END = 6
    PACKET_HTTPC = 7
    PACKET_HTTPC_START = 8
    PACKET_HTTPC_END = 9
    PACKET_ERROR = 10
    PACKET_MSG = 11
    PACKET_REQUEST_END = 255
    
    PACKET_PARAM = 30
    ACTIVE_STACK = 40


class ParamDef(object):
    KEEPALIVE = 1
    AGENT_BOOT_ENV = 2
    CONFIGURE_UPDATE = 3
    CONFIGURE_GET = 4
    COMPO_VERSIONS = 5
    THREAD_LIST = 7
    THREAD_DETAIL = 8
    GET_ACTIVE_STACK = 9
    HEAP_HISTO = 10
    LOADED_CLASS_LIST = 11
    GET_ENV = 12
    SYSTEM_GC = 13
    SET_CONFIG = 14
    OPEN_SOCKET_LIST = 15
    LOADED_CLASS_DETAIL = 16
    LOADED_CLASS_REDEFINE = 17
    
    AGENT_JAR_LIST = 18
    AGENT_JAR_SAVE = 19
    AGENT_JAR_DELETE = 20
    
    RESET_STRING_SENT_MARK = 21
    
    AGENT_LOG_LIST = 22
    AGENT_LOG_READ = 23
    THREAD_CONTROL = 24
    
    GET_ACTIVE_TRANSACTION_LIST = 25
    GET_ACTIVE_TRANSACTION_DETAIL = 26
    
    MODULE_DEPENDENCY = 101


class UdpSession(object):
    s = None
    buffer_arr = []
    thread_lock = threading.Lock()
    
    @classmethod
    def udp(cls):
        import socket
        sock = socket.socket(socket.AF_INET,
                             socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF,
                        PacketEnum.PACKET_BUFFER_MAX_SIZE)
        sock.connect((PacketEnum.SERVER, PacketEnum.PORT))
        cls.s = sock
        
        t = threading.Thread(target=cls.get)
        t.setDaemon(True)
        t.start()
        
        return sock
    
    @classmethod
    def send_packet(cls, packet_type, ctx, datas=[]):
        try:
            if len(b''.join(cls.buffer_arr)) > PacketEnum.PACKET_BUFFER_SIZE:
                cls.send(packet_type, ctx)
            
            if not datas:
                return
            
            dout = DataOutputX()
            start_header_buffer_size = len(dout.buffer.getvalue())
            
            # header
            dout.writeByte(packet_type)
            dout.writeInt(PacketEnum.PACKET_VERSION)
            dout.writeInt(0)
            
            # body
            start_body_buffer_size = len(dout.buffer.getvalue())
            
            if ctx:
                dout.writeLong(ctx.id)
                dout.writeLong(ctx.start_time)
                dout.writeInt(ctx.elapsed)
                dout.writeLong(ctx.getElapsedCpuTime())
                dout.writeLong(ctx.getElapsedMemTime())
                dout.writeLong(ctx.thread_id)
            
            diff = PacketEnum.PACKET_BUFFER_SIZE \
                   - len(b''.join(cls.buffer_arr)) - PacketEnum.PACKET_TEXT_POS
            for data in datas:
                diff -= len(data)
                if diff < 0:
                    data = ' '
                    logging.debug('message too long.', extra={'id': 'WA999'},
                                  exc_info=False)
                dout.writeUTF(data)
            
            with cls.thread_lock:
                dout.writeToPos(
                    start_header_buffer_size + PacketEnum.PACKET_HEADER_LEN_POS,
                    len(dout.buffer.getvalue()) - start_body_buffer_size)
                
                cls.buffer_arr.append(dout.buffer.getvalue())
                
                if not ctx or packet_type == PacketTypeEnum.PACKET_REQUEST \
                        or packet_type == PacketTypeEnum.PACKET_REQUEST_END:
                    cls.send(packet_type, ctx)
        except Exception as e:
            logging.debug(e, extra={'id': 'WA913'}, exc_info=True)
    
    @classmethod
    def send(cls, packet_type, ctx):
        s = cls.s
        if not s:
            s = cls.udp()
        
        try:
            s.sendall(b''.join(cls.buffer_arr))
        except ConnectionRefusedError as e:
            logging.debug(e, extra={'id': 'WA911'}, exc_info=True)
            cls.udp()
        except Exception as e:
            logging.debug(len(b''.join(cls.buffer_arr)))
            cls.buffer_arr.pop()
            logging.debug(len(b''.join(cls.buffer_arr)))
            logging.debug(e, extra={'id': 'WA912'}, exc_info=True)
            cls.send(packet_type, ctx)
            logging.debug('re send!')
        finally:
            cls.buffer_arr = []
            if packet_type == PacketTypeEnum.PACKET_REQUEST_END:
                TraceContextManager.end(ctx.id)
    
    @classmethod
    def get(cls):
        while True:
            try:
                received = cls.s.recv(1024)
                cls.handle(received.decode().split(','))
                time.sleep(1)
            except Exception as e:
                logging.debug(e, extra={'id': 'WA914'}, exc_info=True)
    
    @classmethod
    def handle(cls, received):
        param_id, request, extra = tuple(received)
        param_id = int(param_id)
        
        if not param_id:
            # active stack pack
            datas = []
            data = extra.replace(' ', ', ')

            frame = sys._current_frames().get(
                TraceContextManager.parseThreadId(int(data.split(', ')[0]))[0])
            if not frame:
                return
            
            for stack in traceback.extract_stack(frame):
                line = stack[0]
                line_num = stack[1]
                
                if line.find('whatap/trace') > -1:
                    continue
                data += '{} (line {})\n'.format(line, line_num)
            
            datas.append(data)
        
            cls.send_packet(PacketTypeEnum.ACTIVE_STACK, None, datas)
        else:
            # param pack
            # format: "[packetType], [ctx], [datas: xxxx xxxx xxxx]"
            datas = [str(param_id), request, PARAM_KEY[param_id]]
            if param_id == ParamDef.MODULE_DEPENDENCY:
                import pip
                data = ', '.join(map(str, list(pip.get_installed_distributions())))
                datas.append(data)
            elif param_id == ParamDef.GET_ACTIVE_TRANSACTION_DETAIL:
                data = extra.replace(' ', ', ')
                frame = sys._current_frames().get(
                    TraceContextManager.parseThreadId(int(data.split(', ')[0]))[0])
                if not frame:
                    return
                
                for stack in traceback.extract_stack(frame):
                    line = stack[0]
                    line_num = stack[1]
                    
                    if line.find('whatap/trace') > -1:
                        continue
                    data += '{} (line {})\n'.format(line, line_num)
                
                datas.append(data)
            
            cls.send_packet(PacketTypeEnum.PACKET_PARAM, None, datas)


PARAM_KEY = {
    ParamDef.MODULE_DEPENDENCY: 'module',
    ParamDef.GET_ACTIVE_TRANSACTION_DETAIL: 'detail',
}

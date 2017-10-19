# coding=utf-8
import json
import os
import socket
import subprocess
from logging.handlers import SocketHandler
import select
import datetime
import time
import sys
from struct import pack
from missinglink_kernel.callback.base_callback import RootLoggerSniffer
from missinglink_kernel.callback.monkey_patch_process import MonkeyPatchProcess
from missinglink_kernel.trie import Trie


class ReverseSocketHandler(SocketHandler):
    def __init__(self, sock):
        SocketHandler.__init__(self, '', 0)
        self.closeOnError = 0
        self.sock = sock
        self._log_handler = None

    def shutdown(self):
        self.close()

    def close(self):
        if self.sock is not None:
            self.sock.sendall(pack('!i', 0))
            self.sock.shutdown(socket.SHUT_WR)

        super(ReverseSocketHandler, self).close()

    def makePickle(self, record):
        alt_zone = -time.altzone

        timezone = '%s%02d:%02d' % ('+' if alt_zone > 0 else '-', alt_zone / 3600, alt_zone % 60)
        params = {
            'level': record.levelname,
            'message': record.msg % record.args,
            'category': record.name,
            'ts': datetime.datetime.fromtimestamp(record.created).isoformat() + timezone
        }

        data = (json.dumps(params) + '\n').encode('utf-8')
        val = pack('!i', len(data))

        return val + data

    def makeSocket(self, **kwargs):
        return self.sock


class RemoteLoggerHandler(RootLoggerSniffer):
    def __init__(
            self, session_id, endpoint, log_level, logs_so_far, log_filter=None, terminate_endpoint=None):
        super(RemoteLoggerHandler, self).__init__(log_level)

        self._clients = None

        self.session_id = session_id
        self.log_level = log_level
        server_socket, port = self._start_log_server()

        self._server_socket = server_socket
        self._socket_log_handler = None
        self._logs_so_far = logs_so_far[:]
        self._port = port
        self._terminate_endpoint = terminate_endpoint
        self._endpoint = endpoint
        self._filter_log = None
        self.parse_filter_log(log_filter, log_level)
        self._process = None

        self._activate()

    def __del__(self):
        self.close()

    def parse_filter_log(self, filter_log, global_log_level):
        if filter_log is None:
            filter_log = 'root:%s' % global_log_level

        self._filter_log = Trie()
        for key_val in filter_log.split(';'):
            name, level = key_val.split(':')

            if not name.startswith('root'):
                name = 'root.' + name

            level = int(level)
            self._filter_log[name] = level

    @property
    def port(self):
        return self._port

    def _filter_log_by_name_level(self, name, level):
        if self._filter_log is None:
            return True

        name = name or ''

        if not name.startswith('root'):
            name = 'root.' + name

        parts = name.split('.')

        for i in range(len(parts)):
            try:
                current_name = '.'.join(parts)
                value = self._filter_log[current_name]

                return 0 < value <= level
            except KeyError:
                parts.pop()
                continue

        return True

    def activate_if_needed(self):
        if self._socket_log_handler is None:
            self._check_waiting_clients()

    def on_root_log(self, record):
        self.activate_if_needed()

        if not self._filter_log_by_name_level(record.name, record.levelno):
            return

        if self._socket_log_handler is None:
            self._logs_so_far.append(record)
            return

        self._socket_log_handler.emit(record)

    def start_remote_script(self, disable_process_monkey_patch, is_root=False):
        current_script_dir = os.path.dirname(__file__)
        script_path = os.path.join(current_script_dir, 'log_monitor.py')

        params = [sys.executable, script_path, '--endpoint', self._endpoint, '--port', str(self._port)]

        if self._terminate_endpoint is not None:
            params.append('--terminateEndpoint')
            params.append(self._terminate_endpoint)

        if is_root:
            params.append('--isRoot')

        MonkeyPatchProcess.unmonkey_process_functions(disable_process_monkey_patch)
        try:
            return subprocess.Popen(params)
        finally:
            MonkeyPatchProcess.restore_monkey_process_functions(disable_process_monkey_patch)

    @classmethod
    def _start_log_server(cls):
        server_socket = socket.socket()
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('127.0.0.1', 0))
        server_socket.listen(1)

        port = server_socket.getsockname()[1]

        return server_socket, port

    def _check_waiting_clients(self, timeout=0):
        read_list = [self._server_socket]
        readable, _, _ = select.select(read_list, [], [], timeout)

        if len(readable) == 0:
            return False

        client_socket, address = self._server_socket.accept()

        self._create_socket_log(client_socket)

        return True

    def _create_socket_log(self, sock):
        log_handler = ReverseSocketHandler(sock)

        for record in self._logs_so_far:
            if not self._filter_log_by_name_level(record.name, record.levelno):
                continue

            log_handler.emit(record)

        self._logs_so_far = None
        self._socket_log_handler = log_handler

    def close(self):
        log_handler = self._socket_log_handler
        if log_handler is not None:
            self._socket_log_handler = None
            log_handler.shutdown()

        super(RemoteLoggerHandler, self).close()

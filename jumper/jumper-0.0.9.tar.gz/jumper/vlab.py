"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
from __future__ import print_function
import os
import errno
import sys
import subprocess
import hashlib
from time import sleep
from shutil import copyfile
from shutil import copymode
import json

import timeout_decorator

from .jemu_uart import JemuUart
from .jemu_peripherals_parser import JemuPeripheralsParser
from .jemu_gpio import JemuGpio
from .jemu_connection import JemuConnection
from .jemu_web_api import JemuWebApi
from .jemu_interrupt import JemuInterrupt

DEFAULT_CONFIG = os.path.join(os.path.expanduser('~'), '.jumper', 'config.json')


class EmulationError(Exception):
    pass


class FileNotFoundError(Exception):
    pass


class Vlab(object):
    if os.environ.get('JEMU_DIR') is None:
        _transpiler_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    else:
        _transpiler_dir = os.path.abspath(os.environ['JEMU_DIR'])

    _jemu_build_dir = os.path.abspath(os.path.join(_transpiler_dir, 'emulator', '_build'))
    _jemu_bin_src = os.path.join(_jemu_build_dir, 'jemu')

    _INT_TYPE = "interrupt_type"

    _TYPE_STRING = "type"
    _BKPT = "bkpt"
    _VALUE_STRING = "value"

    def silent_remove_file(self, filename):
        try:
            os.remove(filename)
        except OSError as e:
            if (e.errno != errno.ENOENT):
                raise

    def valid_file_existence(self, file_path, err_name):
        try:
            f = open(file_path)
            f.close()
        except Exception:
            err_str = "Failed to open file \"" + err_name + "\" (at: '" + self._peripherals_json + "')"
            print(err_str)
            sys.exit()

    def __init__(self, working_directory=None, config_file=None, gdb_mode=False, remote_mode=True, sudo_mode=False, print_trace=False, trace_output_file="", print_uart=False, uart_output_file="", debug_port=False):
        self._working_directory = os.path.abspath(working_directory) if working_directory else self._transpiler_dir
        self._remote_mode = remote_mode
        self._gdb_mode = gdb_mode
        self._sudo_mode = sudo_mode
        self._jemu_process = None
        self._was_start = False
        self._transpiler_cmd = ["node", "index.js", "--bin", ""]
        self._peripherals_json = os.path.join(self._working_directory, "peripherals.json")
        self.valid_file_existence(self._peripherals_json, "peripherals.json")
        self._scenario_json = os.path.join(self._working_directory, "scenario.json")
        self.valid_file_existence(self._scenario_json, "scenario.json")
        self._uart_device_path = os.path.join(self._working_directory, 'uart')
        self._jemu_server_address = "localhost"
        self._jemu_server_port = "8000"
        self._jemu_bin = os.path.join(self._working_directory, 'jemu')
        self._cache_file = self._jemu_bin + ".cache.sha1"
        self._uart = JemuUart(self._uart_device_path)
        self._uart.remove()
        self._jemu_connection = JemuConnection(self._jemu_server_address, self._jemu_server_port)
        self._jemu_gpio = JemuGpio(self._jemu_connection)
        self._jemu_interrupt = JemuInterrupt(self._jemu_connection)
        self._peripherals_json_parser = \
            JemuPeripheralsParser(os.path.join(self._working_directory, self._peripherals_json))
        self._build_peripherals_methods()
        self._print_trace = print_trace
        self._trace_output_file = trace_output_file
        self._print_uart = print_uart
        self._uart_output_file = uart_output_file
        self._debug_port = debug_port
        self._on_bkpt = None
        self._return_code = None
        self._jemu_connection.register(self.receive_packet)

        token = None

        if config_file:
            if not os.path.isfile(config_file):
                raise FileNotFoundError('Config file not found at: {}'.format(os.path.abspath(config_file)))
        else:
            if os.path.isfile(DEFAULT_CONFIG):
                config_file = DEFAULT_CONFIG

        if config_file:
            with open(config_file) as config_data:
                config = json.load(config_data)
            if 'token' in config:
                token = config['token']

        if remote_mode:
            self._web_api = JemuWebApi(jumper_token=token)

    @property
    def uart(self):
        return self._uart

    @property
    def gpio(self):
        return self._jemu_gpio

    @property
    def interrupts(self):
        return self._jemu_interrupt

    @property
    def interrupt_type(self):
        return self._INT_TYPE

    def _build_peripherals_methods(self):
        peripherals = self._peripherals_json_parser.get_peripherals(self._jemu_connection)

        for peripheral in peripherals:
            setattr(self, peripheral["name"], peripheral["obj"])
    
    @staticmethod
    def _get_file_signature(file_path):
        sha1 = hashlib.sha1()

        with open(file_path, 'rb') as f:
            while True:
                data = f.read(65536)
                if not data:
                    break
                sha1.update(data)

        return sha1.hexdigest()

    def _read_file_signature_backup(self):
        data = ''
        if os.path.isfile(self._cache_file):
            if os.path.isfile(self._jemu_bin):
                with open(self._cache_file, 'r') as f:
                    data = f.read().replace('\n', '')
            else:
                os.remove(self._cache_file)
        
        return data

    def _write_file_signature_backup(self, sha1_cache_string):
        with open(self._cache_file, 'w+') as f:
            f.write(sha1_cache_string)

    def load(self, file_path):
        if self._remote_mode:
            filename = os.path.basename(file_path)
            gen_new = True
            new_signature = self._get_file_signature(file_path)
            
            prev_signature = self._read_file_signature_backup()
            if prev_signature == new_signature:
                gen_new = False

            if gen_new:
                self.silent_remove_file(self._jemu_bin)
                self.silent_remove_file(self._cache_file)
                with open(file_path, 'r') as data:
                    self._web_api.create_emulator(filename, data, self._jemu_bin)
                    if os.path.isfile(self._jemu_bin):
                        self._write_file_signature_backup(new_signature)

        else:
            self._transpiler_cmd[3] = self._transpiler_cmd[3] + file_path
            subprocess.call(self._transpiler_cmd, cwd=self._transpiler_dir, stdout=open(os.devnull, 'w'), stderr=None)
            copyfile(self._jemu_bin_src, self._jemu_bin)
            copymode(self._jemu_bin_src, self._jemu_bin)

    def start(self, ns=None):
        if not os.path.isfile(self._jemu_bin):
            raise Exception(self._jemu_bin + ' is not found')
        elif not os.access(self._jemu_bin, os.X_OK):
            raise Exception(self._jemu_bin + ' is not executable')

        self._was_start = True

        jemu_cmd = []
        if self._debug_port:
            jemu_cmd = ['gdbserver', 'localhost:7777']
        jemu_cmd.append(self._jemu_bin)
        jemu_cmd.append('-w')
        if self._gdb_mode:
            jemu_cmd.append('-g')
        if self._sudo_mode:
            jemu_cmd.append('-s')
        if self._print_trace:
            jemu_cmd.append('-t')
            if self._trace_output_file != "":
                jemu_cmd.append(self._trace_output_file)
        if self._print_uart:
            jemu_cmd.append('-u')
            if self._uart_output_file != "":
                jemu_cmd.append(self._uart_output_file)

        self._jemu_process = subprocess.Popen(
            jemu_cmd,
            cwd=self._working_directory,
        )
        sleep(0.3)

        @timeout_decorator.timeout(3)
        def wait_for_uart():
            while not os.path.exists(self._uart_device_path):
                sleep(0.1)

        try:
            wait_for_uart()
        except timeout_decorator.TimeoutError:
            self.stop()
            raise EmulationError

        self._uart.open()

        @timeout_decorator.timeout(3)
        def wait_for_connection():
            while not self._jemu_connection.connect():
                sleep(0.1)

        try:
            wait_for_connection()
        except timeout_decorator.TimeoutError:
            self.stop()
            raise EmulationError
        if not self._jemu_connection.handshake(ns):
            raise EmulationError

        self._jemu_connection.start()

    def stop(self):
        self._jemu_connection.close()
        self._uart.close()
        self._uart.remove()

        if self._jemu_process and self._jemu_process.poll() is None:
            self._jemu_process.terminate()
            self._jemu_process.wait()

        self._uart = None
        self._jemu_connection = None

    def run_for_ms(self, ms):
        self.run_for_ns(ms * 1000000)

    def run_for_ns(self, ns):
        if not self._was_start:
            self.start(ns)
            self.SUDO.set_stopped_packet_rec(False)
            self.SUDO.wait_until_stopped()
        else:
            self.SUDO.run_for_ns(ns)

    def stop_after_ms(self, ms):
        self.stop_after_ns(ms*1000000)

    def stop_after_ns(self, ns):
        self.SUDO.stop_after_ns(ns)

    def resume(self):
        self.SUDO.resume()

    def on_interrupt(self, callback):
        self.interrupts.on_interrupt([callback])

    def on_pin_level_event(self, callback):
        self.gpio.on_pin_level_event([callback])

    def on_bkpt(self, callback):
        self._on_bkpt = callback

    def receive_packet(self, jemu_packet):
        if jemu_packet[self._TYPE_STRING] == self._BKPT:
            if self._on_bkpt is not None:
                bkpt_code = jemu_packet[self._VALUE_STRING]
                self._on_bkpt(bkpt_code)


    def is_running(self):
        if not self._jemu_process:
            return False

        self._return_code = self._jemu_process.poll()
        return self._return_code is None

    def get_return_code(self):
        if not self._jemu_process:
            return None
        
        if (self._return_code is None):
            self._return_code = self._jemu_process.poll()
            
        return self._return_code

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *err):
        self.stop()

    def __del__(self):
        pass

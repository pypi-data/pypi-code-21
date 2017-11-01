#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2017 CANDY LINE INC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import fcntl
import json
import os
import socket
import select
import struct
import sys
import termios
import threading
import time
import glob
import platform
import traceback

# SerialPort class was imported from John Wiseman's
# https://github.com/wiseman/arduino-serial/blob/master/arduinoserial.py

# Map from the numbers to the termios constants (which are pretty much
# the same numbers).

BPS_SYMS = {
    115200:   termios.B115200,
    460800:   4100,
    # 230400:   termios.B230400,
    # 57600:    termios.B57600,
    # 38400:    termios.B38400,
    # 19200:    termios.B19200,
    # 9600:     termios.B9600,
    # 921600:   4103
    }


# Indices into the termios tuple.

IFLAG = 0
OFLAG = 1
CFLAG = 2
LFLAG = 3
ISPEED = 4
OSPEED = 5
CC = 6


def bps_to_termios_sym(bps):
    return BPS_SYMS[bps]

# For local debugging:
# import candy_board_qws
# serial = candy_board_qws.SerialPort("/dev/ttyUSB2", 115200)
# server = candy_board_qws.SockServer(
#     "1.0.0",
#     "/var/run/candy-board-service.sock", serial)
# server.debug = True
# server.apn_ls()

# looking for a modem serial port
# import candy_board_qws
# candy_board_qws.SerialPort.resolve_modem_port()


class SerialPort(object):

    def __init__(self, serialport, bps):
        """Takes the string name of the serial port
        (e.g. "/dev/tty.usbserial","COM1") and a baud rate (bps) and
        connects to that port at that speed and 8N1. Opens the port in
        fully raw mode so you can send binary data.
        """
        self.fd = os.open(serialport, os.O_RDWR | os.O_NOCTTY | os.O_NDELAY)
        attrs = termios.tcgetattr(self.fd)
        bps_sym = bps_to_termios_sym(int(bps))
        # Set I/O speed.
        attrs[ISPEED] = bps_sym
        attrs[OSPEED] = bps_sym

        # 8N1
        attrs[CFLAG] &= ~termios.PARENB
        attrs[CFLAG] &= ~termios.CSTOPB
        attrs[CFLAG] &= ~termios.CSIZE
        attrs[CFLAG] |= termios.CS8
        # No flow control
        attrs[CFLAG] &= ~termios.CRTSCTS

        # Turn on READ & ignore contrll lines.
        attrs[CFLAG] |= termios.CREAD | termios.CLOCAL
        # Turn off software flow control.
        attrs[IFLAG] &= ~(termios.IXON | termios.IXOFF | termios.IXANY)

        # Make raw.
        attrs[LFLAG] &= ~(termios.ICANON | termios.ECHO |
                          termios.ECHOE | termios.ISIG)
        attrs[OFLAG] &= ~termios.OPOST

        # It's complicated--See
        # http://unixwiz.net/techtips/termios-vmin-vtime.html
        attrs[CC][termios.VMIN] = 0
        attrs[CC][termios.VTIME] = 20
        termios.tcsetattr(self.fd, termios.TCSANOW, attrs)

        self.ping()

    def available(self):
        return True

    def read_until(self, until):
        buf = ""
        done = False
        cnt = 0
        while not done:
            n = os.read(self.fd, 1)
            if n == '':
                if cnt > 200:
                    buf = None
                    break
                cnt = cnt + 1
                # FIXME: Maybe worth blocking instead of busy-looping?
                time.sleep(0.01)
                continue
            buf = buf + n
            if n == until:
                done = True
        return buf

    def read_line(self):
        try:
            return self.read_until("\n").strip()
        except OSError:
            return None

    def write(self, str):
        os.write(self.fd, str)

    def write_byte(self, byte):
        os.write(self.fd, chr(byte))

    def close(self):
        try:
            os.close(self.fd)
        except OSError:
            pass

    def ping(self, loop=3):
        ret = None
        for i in (0, loop):
            self.write("AT\r")
            time.sleep(0.1)
            line = self.read_line()
            if line is None:
                time.sleep(0.1)
                continue
            else:
                ret = ''
                while line is not None:
                    ret = ret + line + '\r'
                    line = self.read_line()
                break
        return ret

    @staticmethod
    def resolve_modem_baudrate(p):
        if platform.system() != 'Linux':
            return None

        for bps in BPS_SYMS.keys():
            port = SerialPort.open_serial_port(p, bps)
            if port is None:
                continue
            ret = port.ping()
            if ret is None:
                port.close()
                continue
            if "OK" in ret:
                port.close()
                return bps
            port.close()

        return None

    @staticmethod
    def open_serial_port(p, bps):
        for i in (0, 3):
            port = None
            try:
                port = SerialPort(p, bps)
                return port
            except Exception:
                if port:
                    try:
                        port.close()
                    except Exception:
                        pass
                port = None
                time.sleep(0.1)
                pass
        return None

    @staticmethod
    def resolve_modem_port(bps=115200):
        if platform.system() != 'Linux':
            return None

        for t in [
                    '/dev/QWS.*.MODEM',
                    '/dev/ttyUSB*',
                    '/dev/ttySC*'
                ]:
            for p in sorted(glob.glob(t)):
                port = SerialPort.open_serial_port(p, bps)
                if port is None:
                    continue
                ret = port.ping()
                if ret is None:
                    port.close()
                    continue
                if "OK" in ret:
                    port.close()
                    return p
                port.close()

        return None


class LazySerialPort:
    def __init__(self, serialport, bps):
        self.serial = None
        self.serialport = serialport
        self.bps = bps

    def _serial(self):
        if self.serial is None:
            self.serial = SerialPort(self.serialport, self.bps)
        return self.serial

    def available(self):
        try:
            self._serial()
            return True
        except OSError:
            return False

    def read_line(self):
        return self._serial().read_line()

    def write(self, str):
        return self._serial().write(str)

    def write_byte(self, byte):
        return self._serial().write_byte(byte)

    def close(self):
        if self.serial is None:
            return
        try:
            return self.serial.close()
        finally:
            self.serial = None


class SockServer(threading.Thread):
    def __init__(self, version,
                 sock_path="/var/run/candy-board-service.sock", serial=None):
        super(SockServer, self).__init__()
        self.version = version
        self.sock_path = sock_path
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.serial = serial
        self.debug = False

    def recv(self, connection, size):
        ready, _, _ = select.select([connection], [], [], 5)
        if ready:
            return connection.recv(size)
        else:
            raise IOError("recv Timeout")

    def run(self):
        self.sock.bind(self.sock_path)
        self.sock.listen(128)
        header_packer = struct.Struct("I")
        print("Listening to the socket[%s]...." % self.sock_path)

        while True:
            try:
                connection, client_address = self.sock.accept()
                connection.setblocking(0)

                # request
                header = self.recv(connection, header_packer.size)
                size = header_packer.unpack(header)
                unpacker_body = struct.Struct("%is" % size)
                cmd_json = self.recv(connection, unpacker_body.size)
                cmd = json.loads(cmd_json)

                # response
                message = self.perform(cmd)
                if message:
                    size = len(message)
                else:
                    size = 0
                packed_header = header_packer.pack(size)
                connection.sendall(packed_header)
                if size > 0:
                    packer_body = struct.Struct("%is" % size)
                    packed_message = packer_body.pack(message)
                    connection.sendall(packed_message)

            except Exception:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback)

            finally:
                if 'connection' in locals():
                    connection.close()

    def perform(self, cmd):
        if self.serial is None or self.serial.available() is False:
            return self.error_message("Modem is not ready")
        try:
            if cmd['category'][0] == '_':
                raise AttributeError()
            m = getattr(self.__class__,
                        "%s_%s" % (cmd['category'], cmd['action']))
            return m(self, cmd)
        except AttributeError:
            return self.error_message("Unknown Command")
        except KeyError:
            return self.error_message("Invalid Args")
        except OSError:
            return self.error_message("I/O Error")
        except Exception:
            return self.error_message("Unexpected error: %s" %
                                      (''.join(traceback
                                       .format_exception(*sys.exc_info())[-2:])
                                       .strip().replace('\n', ': '))
                                      )

    def error_message(self, msg):
        return json.dumps({"status": "ERROR", "result": msg})

    def read_line(self):
        line = self.serial.read_line()
        if self.debug:
            print("[modem:IN] => [%s]" % line)
        return line

    def send_at(self, cmd, ok="OK"):
        line = "%s\r" % cmd
        if self.debug:
            print("[modem:OUT] => [%s]" % line)
        self.serial.write(line)
        time.sleep(0.1)
        result = ""
        status = None
        count = 0
        while True:
            line = self.read_line()
            if line is None:
                if status is not None or count > 650:
                    break
                time.sleep(0.1)
                count = count + 1
            elif line == cmd:
                continue
            elif line == ok or line == "ERROR":
                status = line
            elif line is None:
                status = "UNKNOWN"
            elif line.strip() != "":
                result += line + "\n"
        if self.debug:
            print("cmd:[%s] => status:[%s], result:[%s]" %
                  (cmd, status, result))
        return (status, result.strip())

    def _apn_ls(self):
        status, result = self.send_at("AT+CGDCONT?")
        apn_list = []
        id_name_list = []
        if status == "OK":
            try:
                id_name_list = map(lambda e: e[10:].split(",")[0] + "," +
                                   e[10:].split(",")[2].translate(None, '"'),
                                   result.split("\n"))
                status, result = self.send_at("AT$QCPDPP?")
                creds_list = []
                if status == "OK":
                    def to_user(e):
                        if len(e) > 2:
                            return e[2].translate(None, '"')
                        return ''
                    creds_list = map(lambda e: to_user(e),
                                     map(lambda e: e[9:].split(","),
                                         result.split("\n")))
            except IndexError:
                pass
        for i in range(len(id_name_list)):
                id_name = id_name_list[i].split(",")
                apn = {
                    'apn_id': id_name[0],
                    'apn': id_name[1]
                }
                if creds_list[i]:
                    apn['user'] = creds_list[i]
                apn_list.append(apn)
        message = {
            'status': status,
            'result': {
                'apns': apn_list
            }
        }
        return message

    def apn_ls(self, cmd={}):
        return json.dumps(self._apn_ls())

    def apn_set(self, cmd={}):
        (name, user_id, password) = (cmd['name'], cmd['user_id'],
                                     cmd['password'])
        apn_id = "1"
        if 'id' in cmd:
            apn_id = cmd['id']
        status, result = self.send_at(("AT+CGDCONT=%s,\"IP\",\"%s\"," +
                                      "\"0.0.0.0\",0,0") % (apn_id, name))
        if status == "OK":
            status, result = self.send_at(("AT$QCPDPP=%s,3,\"%s\",\"%s\"") %
                                          (apn_id, password, user_id))
        message = {
            'status': status,
            'result': result
        }
        return json.dumps(message)

    def _apn_del(self, apn_id):
        # removes QCPDPP as well
        status, result = self.send_at(("AT+CGDCONT=%s") % apn_id)
        message = {
            'status': status,
            'result': result
        }
        return message

    def apn_del(self, cmd={}):
        apn_id = "1"
        if 'id' in cmd:
            apn_id = cmd['id']
        return json.dumps(self._apn_del(apn_id))

    def network_show(self, cmd={}):
        rssi = ""
        network = "UNKNOWN"
        rssi_desc = ""
        operator = "UNKNOWN"
        status, result = self.send_at("AT+CSQ")
        if status == "OK":
            rssi_level = int(result[5:].split(",")[0])
            if rssi_level == 0:
                rssi = "-113"
                rssi_desc = "OR_LESS"
            elif rssi_level == 1:
                rssi = "-111"
            elif rssi_level <= 30:
                rssi = "%i" % (-109 + (rssi_level - 2) * 2)
            elif rssi_level == 31:
                rssi = "-51"
                rssi_desc = "OR_MORE"
            elif rssi_level == 100:
                rssi = "-116"
                rssi_desc = "OR_LESS"
            elif rssi_level == 101:
                rssi = "-115"
            elif rssi_level <= 190:
                rssi = "%i" % (-114 + (rssi_level - 102))
            elif rssi_level == 191:
                rssi = "-25"
                rssi_desc = "OR_MORE"
            else:
                rssi_desc = "NO_SIGANL"
            status, result = self.send_at("AT+CPAS")
            if status == "OK":
                state_level = int(result[6:])
                if state_level == 4:
                    network = "ONLINE"
                else:
                    network = "OFFLINE"
                if status == "OK":
                    status, result = self.send_at("AT+COPS?")
                    operator = result.split(',')[2][1:-1]
        message = {
            'status': status,
            'result': {
                'rssi': rssi,
                'rssiDesc': rssi_desc,
                'network': network,
                'operator': operator
            }
        }
        return json.dumps(message)

    def sim_show(self, cmd={}):
        state = "SIM_STATE_ABSENT"
        msisdn = ""
        imsi = ""
        status, result = self.send_at("AT+CIMI")
        if status == "OK":
            imsi = result
            state = "SIM_STATE_READY"
            status, result = self.send_at("AT+CNUM")
            if len(result) > 5:
                msisdn = result[6:].split(",")[1].translate(None, '"')
            else:
                msisdn = ''
        message = {
            'status': status,
            'result': {
                'msisdn': msisdn,
                'imsi': imsi,
                'state': state
            }
        }
        return json.dumps(message)

    def _counter_show(self):
        """
        - Show TX/RX packet counter
        """
        status, result = self.send_at("AT+QGDCNT?")
        tx = '0'
        rx = '0'
        if status == "OK":
            txrx = result.split(':')[1].strip().split(',')
            tx = txrx[0]
            rx = txrx[1]
        message = {
            'status': status,
            'result': {
                'tx': tx,
                'rx': rx
            }
        }
        return message

    def _counter_reset(self):
        """
        - Reset packet counter
        """
        status, result = self.send_at("AT+QGDCNT=0")
        message = {
            'status': status,
            'result': result
        }
        return message

    def _imei_show(self):
        """
        - Show IMEI
        """
        status, result = self.send_at("AT+GSN")
        message = {
            'status': status,
            'result': result
        }
        return message

    def _timestamp_show(self):
        """
        - Show timestamp
        """
        status, result = self.send_at("AT+CCLK?")
        message = {
            'status': status,
            'result': result
        }
        return message

    def modem_show(self, cmd={}):
        status, result = self.send_at("ATI")
        man = "UNKNOWN"
        mod = "UNKNOWN"
        rev = "UNKNOWN"
        imei = "UNKNOWN"
        counter = None
        utc = None
        timezone_hrs = None
        if status == "OK":
            info = result.split("\n")
            man = info[0]
            mod = info[1]
            rev = info[2][10:]
            result = self._imei_show()
            if result['status'] == "OK":
                imei = result['result']
            result = self._counter_show()
            if result['status'] == "OK":
                counter = result['result']
            result = self._timestamp_show()
            if result['status'] == "OK":
                utc = result['result'][8:-4]
                timezone_hrs = float(result['result'][-4:-1]) / 4
        message = {
            'status': status,
            'result': {
                'manufacturer': man,
                'model': mod,
                'revision': rev,
                'imei': imei,
                'datetime': utc,
                'timezone': timezone_hrs
            }
        }
        if counter:
            message['result']['counter'] = counter
        return json.dumps(message)

    def _parse_opts(self, cmd={}):
        opts = {}
        if 'opts' in cmd:
            try:
                opts = json.loads(cmd['opts'])
            except Exception:
                try:
                    entries = map(lambda e: e.split('='),
                                  cmd['opts'].split(','))
                    for (k, v) in entries:
                        opts[k.strip()] = v.strip()
                except Exception:
                    pass
        return opts

    def modem_reset(self, cmd={}):
        """
        - opts counter=yes
            - Reset packet counter
        - no-opts or counter!=yes
            - Reset packet counter
            - Remove all APN
        """
        result = 'counter'
        counter_reset_ret = self._counter_reset()
        status = counter_reset_ret['status']
        opts = self._parse_opts(cmd)
        if 'counter' not in opts or opts['counter'] != 'yes':
            result = ''
            apn_ls_ret = self._apn_ls()
            status = apn_ls_ret['status']
            if apn_ls_ret['status'] == "OK":
                apns = apn_ls_ret['result']['apns']
                for apn in apns:
                    self._apn_del(apn['apn_id'])
        message = {
            'status': status,
            'result': result
        }
        return json.dumps(message)

    def modem_off(self, cmd={}):
        """
        PRIVATE COMMAND (not available from CLI)
        - Power off
        """
        status, result = self.send_at("AT+QPOWD", "POWERED DOWN")
        if status == "POWERED DOWN":
            status = "OK"
            result = ""
        message = {
            'status': status,
            'result': result
        }
        return json.dumps(message)

    def modem_init(self, cmd={}):
        """
        PRIVATE COMMAND (not available from CLI)
        - Enable automatic timezone update with NITZ
          to set modem RTC (if NW is capable)
          Enabled by default.
        - Set baudrate (optional)
        - Reset packet counter (optional)
        """
        if 'tz_update' not in cmd or cmd['tz_update'] is True:
            status, result = self.send_at("AT+CTZU?")
            if status != "OK":
                message = {
                    'status': status,
                    'result': result,
                    'cmd': 'tz_update'
                }
                return json.dumps(message)
            for at in ["AT+COPS=2", "AT+CTZU=1", "AT+COPS=0"]:
                status, result = self.send_at(at)
                if status != "OK":
                    break
        if 'baudrate' in cmd:
            status, result = self.send_at("AT+IPR=%s" % cmd['baudrate'])
            if status != "OK":
                message = {
                    'status': status,
                    'result': result,
                    'cmd': 'baudrate'
                }
                return json.dumps(message)
        if 'counter_reset' in cmd and cmd['counter_reset']:
            counter_reset_ret = self._counter_reset()
            status = counter_reset_ret['status']
            result = counter_reset_ret['result']
        message = {
            'status': status,
            'result': result
        }
        return json.dumps(message)

    def service_version(self, cmd={}):
        message = {
            'status': 'OK',
            'result': {
                'version': self.version,
            }
        }
        return json.dumps(message)

#! /bin/python

import time
import struct
import socket
import logging

logger = logging.getLogger(__package__+'.'+__name__)
logger.setLevel(logging.WARNING)
logger.propagate = False
loghandler = logging.StreamHandler()
loghandler.setLevel(logging.WARNING)
loghandler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
logger.addHandler(loghandler)


SOH = b'\x01'
ACK = b'\x06'

port = 57172


class BadSOHError(Exception):
    strerror = 'Bad SOH is replied. "serial_number" might be wrong.'

class IncompleteResponceError(Exception):
    strerror = 'Responce is incomplete. Please try again.'
    
    def __init__(self, msg):
        self.strerror += msg
        pass


def encode_serialnumber(number_hex_string):
    number = int(number_hex_string, 16)
    number_bytes = struct.pack('<I', number)
    return number_bytes

def encode_datasize(data_bytes):
    dlen = len(data_bytes)
    dlen_bytes = struct.pack('<H', dlen)
    return dlen_bytes

def decode_datasize(size_bytes):
    dlen = struct.unpack('<H', size_bytes)[0]
    return dlen

def encode_checksum(data_bytes):
    dsum = sum(data_bytes)
    dsum_bytes = struct.pack('<H', dsum)
    return dsum_bytes

def verify_checksum(data_bytes, checksum_bytes):
    dsum = sum(data_bytes)
    checksum = struct.unpack('<H', checksum_bytes)[0]
    
    if dsum != checksum: return False
    return True

def verify_soh(soh_bytes):
    return soh_bytes == SOH
    

def connect(host, timeout):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    sock.settimeout(timeout)
    logger.debug('connected to {host}:{port}'.format(**locals(), **globals()))
    return sock

def close(sock):
    sock.close()
    time.sleep(0.01)
    return

def send(sock, serial_number, command, subcommand, data):
    datasize = encode_datasize(data)
    msg_command = SOH + command + subcommand + datasize + data
    command_checksum = encode_checksum(msg_command)
    msg_command += command_checksum
    
    serialnumber_bytes = encode_serialnumber(serial_number)
    commandsize = encode_datasize(msg_command)
    msg = serialnumber_bytes + commandsize + msg_command
    
    serial_ = serialnumber_bytes.hex()
    comsize_ = commandsize.hex()
    soh_ = SOH.hex()
    com_ = command.hex()
    subcom_ = subcommand.hex()
    datasize_ = datasize.hex()
    data_ = data.hex()
    com_checksum_ = command_checksum.hex()
    info_msg = '{serial_} {comsize_} {soh_} {com_} {subcom_}'.format(**locals())
    info_msg += ' {datasize_} {data_} {com_checksum_}'.format(**locals())
    logger.info('sending... {info_msg}'.format(**locals()))
    
    msg_ = msg.hex()
    logger.debug('sending... {msg_}'.format(**locals()))
    sock.send(msg)
    return

def recv(sock):
    def _recv(sock):
        ret = sock.recv(1)
        ret_ = ret.hex()
        logger.debug('received : {ret_}'.format(**locals())) 
        return ret
    
    drecv = b''
    
    soh = _recv(sock)
    soh_ = soh.hex()
    if not verify_soh(soh):
        emsg = 'bad soh : {soh_}'.format(**locals())
        logger.error(emsg)
        raise BadSOHError(emsg)
        return
    drecv += soh
    
    cmd = _recv(sock)
    cmd_ = cmd.hex()
    drecv += cmd
    
    res = _recv(sock)
    res_ = res.hex()
    drecv += res
    
    dlen = b''
    dlen += _recv(sock)
    dlen += _recv(sock)
    dlen_ = dlen.hex()
    drecv += dlen
    dlen_int = decode_datasize(dlen)
    
    data = b''
    for i in range(dlen_int):
        data += _recv(sock)
        continue
    data_ = data.hex()
    drecv += data
    
    checksum = b''
    checksum += _recv(sock)
    checksum += _recv(sock)
    checksum_ = checksum.hex()
    if not verify_checksum(drecv, checksum):
        emsg = 'bad checksum : {checksum_}'.format(**locals())
        logger.error(emsg)
        raise IncompleteResponceError(emsg)
        return        
    drecv += checksum
    
    info_msg = '{soh_} {cmd_} {res_} {dlen_} {data_} {checksum_}'.format(**locals())
    logger.info('received {info_msg}'.format(**locals()))        
    
    drecv_ = drecv.hex()
    logger.debug('received {drecv_}'.format(**locals()))        
    return soh, cmd, res, dlen, data, checksum



def get_current(host, serial_number, timeout=2):
    command = b'\x33'
    subcommand = b'\x00'
    send_data = b'\x00' * 4
    
    sock = connect(host, timeout)
    send(sock, serial_number, command, subcommand, send_data)
    soh, cmd, res, dlen, data, checksum = recv(sock)
    close(sock)
    
    if cmd != command:
        cmd_ = cmd.hex()
        emsg = 'bad command : {cmd_}'.format(**locals())
        logger.error(emsg)
        raise IncompleteResponceError(emsg)
    
    if res != ACK:
        res_ = res.hex()
        emsg = 'bad resopnse : {res_}'.format(**locals())
        logger.error(emsg)
        raise IncompleteResponceError(emsg)
    
    ret = {
        'data1': struct.unpack('<H', data[:2])[0],
        'data2': struct.unpack('<H', data[2:4])[0],
    }
    return ret


def get_record_number(host, serial_number, timeout=2):
    command = b'\x34'
    subcommand = b'\x00'
    send_data = b'\x00' * 4
    
    sock = connect(host, timeout)
    send(sock, serial_number, command, subcommand, send_data)
    soh, cmd, res, dlen, data, checksum = recv(sock)
    close(sock)
    
    if cmd != command:
        cmd_ = cmd.hex()
        emsg = 'bad command : {cmd_}'.format(**locals())
        logger.error(emsg)
        raise IncompleteResponceError(emsg)
    
    if res != ACK:
        res_ = res.hex()
        emsg = 'bad resopnse : {res_}'.format(**locals())
        logger.error(emsg)
        raise IncompleteResponceError(emsg)
    
    ret = {
        'record_number': struct.unpack('<H', data[:2])[0],
    }
    return ret
    

def get_machine_code(host, serial_number, timeout=2):
    command = b'\x35'
    subcommand = b'\x00'
    send_data = b'\x00' * 4
    
    sock = connect(host, timeout)
    send(sock, serial_number, command, subcommand, send_data)
    soh, cmd, res, dlen, data, checksum = recv(sock)
    close(sock)
    
    if cmd != command:
        cmd_ = cmd.hex()
        emsg = 'bad command : {cmd_}'.format(**locals())
        logger.error(emsg)
        raise IncompleteResponceError(emsg)
    
    if res != ACK:
        res_ = res.hex()
        emsg = 'bad resopnse : {res_}'.format(**locals())
        logger.error(emsg)
        raise IncompleteResponceError(emsg)
    
    ret = {
        'machine_code': data[:2],
        'ch1_type': data[2:3],
        'ch2_type': data[3:4],
    }
    return ret


def get_machine_name(host, serial_number, timeout=2):
    command = b'\x36'
    subcommand = b'\x00'
    send_data = b'\x00' * 4
    
    sock = connect(host, timeout)
    send(sock, serial_number, command, subcommand, send_data)
    soh, cmd, res, dlen, data, checksum = recv(sock)
    close(sock)
    
    if cmd != command:
        cmd_ = cmd.hex()
        emsg = 'bad command : {cmd_}'.format(**locals())
        logger.error(emsg)
        raise IncompleteResponceError(emsg)
    
    if res != ACK:
        res_ = res.hex()
        emsg = 'bad resopnse : {res_}'.format(**locals())
        logger.error(emsg)
        raise IncompleteResponceError(emsg)
    
    ret = {
        'machine_name': data[:7].decode('ascii'),
    }
    return ret
    

def set_unit(host, serial_number, unit_flag, timeout=2):
    command = b'\x37'
    subcommand = b'\x00'
    send_data = struct.pack('<B', unit_flag) + (b'\x00' * 3)
    
    sock = connect(host, timeout)
    send(sock, serial_number, command, subcommand, send_data)
    soh, cmd, res, dlen, data, checksum = recv(sock)
    close(sock)
    
    if cmd != command:
        cmd_ = cmd.hex()
        emsg = 'bad command : {cmd_}'.format(**locals())
        logger.error(emsg)
        raise IncompleteResponceError(emsg)
    
    if res != ACK:
        res_ = res.hex()
        emsg = 'bad resopnse : {res_}'.format(**locals())
        logger.error(emsg)
        raise IncompleteResponceError(emsg)
    
    ret = {}
    return ret


def set_display(host, serial_number, display_flag, timeout=2):
    command = b'\x38'
    subcommand = b'\x00'
    send_data = struct.pack('<B', display_flag) + (b'\x00' * 3)
    
    sock = connect(host, timeout)
    send(sock, serial_number, command, subcommand, send_data)
    soh, cmd, res, dlen, data, checksum = recv(sock)
    close(sock)
    
    if cmd != command:
        cmd_ = cmd.hex()
        emsg = 'bad command : {cmd_}'.format(**locals())
        logger.error(emsg)
        raise IncompleteResponceError(emsg)
    
    if res != ACK:
        res_ = res.hex()
        emsg = 'bad resopnse : {res_}'.format(**locals())
        logger.error(emsg)
        raise IncompleteResponceError(emsg)
    
    ret = {}
    return ret


def get_battery(host, serial_number, timeout=2):
    command = b'\x39'
    subcommand = b'\x00'
    send_data = b'\x00' * 4
    
    sock = connect(host, timeout)
    send(sock, serial_number, command, subcommand, send_data)
    soh, cmd, res, dlen, data, checksum = recv(sock)
    close(sock)
    
    if cmd != command:
        cmd_ = cmd.hex()
        emsg = 'bad command : {cmd_}'.format(**locals())
        logger.error(emsg)
        raise IncompleteResponceError(emsg)
    
    if res != ACK:
        res_ = res.hex()
        emsg = 'bad resopnse : {res_}'.format(**locals())
        logger.error(emsg)
        raise IncompleteResponceError(emsg)
    
    ret = {
        'volt': struct.unpack('<H', data[:2])[0],
        'level': struct.unpack('<B', data[2:3])[0],
    }
    return ret


def get_rom_revision(host, serial_number, timeout=2):
    command = b'\x72'
    subcommand = b'\x00'
    send_data = b'\x00' * 4
    
    sock = connect(host, timeout)
    send(sock, serial_number, command, subcommand, send_data)
    soh, cmd, res, dlen, data, checksum = recv(sock)
    close(sock)
    
    if cmd != command:
        cmd_ = cmd.hex()
        emsg = 'bad command : {cmd_}'.format(**locals())
        logger.error(emsg)
        raise IncompleteResponceError(emsg)
    
    if res != ACK:
        res_ = res.hex()
        emsg = 'bad resopnse : {res_}'.format(**locals())
        logger.error(emsg)
        raise IncompleteResponceError(emsg)
    
    ret = {
        'version': struct.unpack('<B', data[:1])[0],
    }
    return ret


def get_mac_addr(host, serial_number, timeout=2):
    command = b'\x6e'
    subcommand = b'\x00'
    send_data = b'\x00' * 4
    
    sock = connect(host, timeout)
    send(sock, serial_number, command, subcommand, send_data)
    soh, cmd, res, dlen, data, checksum = recv(sock)
    close(sock)
    
    if cmd != command:
        cmd_ = cmd.hex()
        emsg = 'bad command : {cmd_}'.format(**locals())
        logger.error(emsg)
        raise IncompleteResponceError(emsg)
    
    if res != ACK:
        res_ = res.hex()
        emsg = 'bad resopnse : {res_}'.format(**locals())
        logger.error(emsg)
        raise IncompleteResponceError(emsg)
    
    ret = {
        'mac_address': data.hex(),
    }
    return ret



class tr7nw(object):
    def __init__(self, host, serial_number, timeout=2):
        self.serial_number = serial_number
        self.host = host
        self.timeout = timeout
        self.download_config()
        pass
        
    def download_config(self):
        d = {}
        d.update(get_record_number(self.host, self.serial_number, self.timeout))
        d.update(self.get_machine_code())
        d.update(get_machine_name(self.host, self.serial_number, self.timeout))
        d.update(get_battery(self.host, self.serial_number, self.timeout))
        d.update(get_rom_revision(self.host, self.serial_number, self.timeout))
        d.update(get_mac_addr(self.host, self.serial_number, self.timeout))
        self.config = d
        return
        
    def get_current(self):
        d = get_current(self.host, self.serial_number, self.timeout)
        d1 = (d['data1'] / 10.) - 100
        d2 = (d['data2'] / 10.) - 100
        data = [
            {'value': d1, 'unit': self.config['ch1_unit']},
            {'value': d2, 'unit': self.config['ch2_unit']},
        ]
        return data
        
    def get_record_number(self):
        d = get_record_number(self.host, self.serial_number, self.timeout)
        return d['record_number']
    
    def get_machine_code(self):
        code2name = {
            b'\x93\x04': 'TR-71wf',
            b'\x94\x04': 'TR-72wf',
            b'\x98\x04': 'TR-71nw',
            b'\x99\x04': 'TR-72nw',
        }
        
        flag2type = {
            b'\x0d': 'C',
            b'\x0e': 'F',
            b'\xd1': '%',
        }
        
        d = get_machine_code(self.host, self.serial_number, self.timeout)
        d['machine_name'] = code2name[d['machine_code']]
        d['ch1_unit'] = flag2type[d['ch1_type']]
        d['ch2_unit'] = flag2type[d['ch2_type']]
        return d
        
    def get_machine_name(self):
        d = get_machine_name(self.host, self.serial_number, self.timeout)
        return d['machine_name']
    
    def get_battery(self):
        d = get_battery(self.host, self.serial_number, self.timeout)
        return d
        
    def get_rom_version(self):
        d = get_rom_version(self.host, self.serial_number, self.timeout)
        return d['version']

    def get_mac_addr(self):
        d = get_mac_addr(self.host, self.serial_number, self.timeout)
        return d['mac_address']
    

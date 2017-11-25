import os
import socket
import subprocess
import logging

from . import config

def _read_file(file_path):
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'r') as info_file:
        return info_file.read().strip()

def get_machine_id():
    return _read_file('/etc/machine-id')

def get_serial():
    # Extract serial from cpuinfo file
    with open('/proc/cpuinfo', 'r') as cpuinfo_file:
        for line in cpuinfo_file:
            if line[0:6] == 'Serial':
                return line[10:26]
    return "0000000000000000"

def get_hostname():
    return socket.gethostname()

def get_local_ip():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(5)
    client.connect(("8.8.8.8", 53))
    local_ip = client.getsockname()[0]
    client.close()
    return local_ip

def get_macs():
    result = {}
    root_dir = '/sys/class/net'
    interfaces = os.listdir(root_dir)
    for interface in interfaces:
        if interface == 'lo' or interface.startswith('br') or interface.startswith('docker') or interface.startswith('veth'):
            continue
        with open(os.path.join(root_dir, interface, 'address'), 'r') as interface_file:
            result[interface] = interface_file.read().strip()
    return result

def get_ssid():
    try:
        ssid = subprocess.check_output('iwgetid -r', shell=True)
    except subprocess.CalledProcessError:
        return None
    return ssid.decode().strip()

def get_temp():
    temp_raw = int(_read_file("/sys/class/thermal/thermal_zone0/temp"))
    temp = float(temp_raw / 1000.0)
    return temp

def get_signal_level():
    wireless_data = _read_file("/proc/net/wireless")
    lines = wireless_data.split("\n")
    if len(lines) < 3:
        return None
    last_line = lines[-1]
    values = last_line.split()
    if len(values) < 4:
        return None
    return int(float(values[3]))

def get_written_kbytes():
    device_path = '/sys/fs/ext4/mmcblk0p2'
    stat_files = ['session_write_kbytes', 'lifetime_write_kbytes']
    data = None
    for stat_file in stat_files:
        written = _read_file(os.path.join(device_path, stat_file))
        if written:
            data = {} if not data else data
            data[stat_file.split('_')[0]] = int(written)
    return data

def get_uptime():
    uptime_data = _read_file('/proc/uptime')
    return float(uptime_data.split()[0])

def get_kernel():
    return {
        'release': _read_file('/proc/sys/kernel/osrelease'),
        'version': _read_file('/proc/sys/kernel/version'),
    }

def save_secret(secret):
    path = config.SECRET_PATH
    base_path = os.path.dirname(path)
    os.makedirs(base_path, exist_ok=True)
    with open(path, 'w') as secret_file:
        secret_file.write(secret)
        return True

def load_secret():
    path = config.SECRET_PATH
    try:
        with open(path, 'r') as secret_file:
            secret = secret_file.read()
            return secret.strip()
    except FileNotFoundError as err:
        logging.error(err)
        return None

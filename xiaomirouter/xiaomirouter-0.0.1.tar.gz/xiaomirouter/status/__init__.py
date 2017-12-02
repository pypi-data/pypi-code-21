""" Status representation of the router """
from xiaomirouter.status.count import create_count_from_json
from xiaomirouter.status.cpu import create_cpu_from_json
from xiaomirouter.status.dev import create_dev_from_json
from xiaomirouter.status.hardware import create_hardware_from_json
from xiaomirouter.status.mem import create_mem_from_json
from xiaomirouter.status.wan import create_wan_from_json


class Status(object):
    """ Status of the router"""

    def __init__(self, dev, code, mem, temperature, count, hardware, up_time,
                 cpu, wan):
        self._dev = dev
        self._code = code
        self._mem = mem
        self._temperature = temperature
        self._count = count
        self._hardware = hardware
        self._up_time = up_time
        self._cpu = cpu
        self._wan = wan

    def get_dev(self):
        return self._dev

    def get_code(self):
        return self._code

    def get_mem(self):
        return self._mem

    def get_temperature(self):
        return self._temperature

    def get_count(self):
        return self._count

    def get_hardware(self):
        return self._hardware

    def get_up_time(self):
        return self._up_time

    def get_cpu(self):
        return self._cpu

    def get_wan(self):
        return self._wan


def create_status_from_json(json_entry):
    devs = []
    for dev in json_entry['dev']:
        devs.append(create_dev_from_json(dev))
    mem = create_mem_from_json(json_entry['mem'])
    count = create_count_from_json(json_entry['count'])
    hardware = create_hardware_from_json(json_entry['hardware'])
    cpu = create_cpu_from_json(json_entry['cpu'])
    wan = create_wan_from_json(json_entry['wan'])
    return Status(devs, json_entry['code'], mem, json_entry['temperature'],
                  count, hardware, json_entry['upTime'], cpu, wan)

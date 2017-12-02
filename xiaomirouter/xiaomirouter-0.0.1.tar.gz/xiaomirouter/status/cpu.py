""" Router CPU information """


class Cpu(object):
    """ Router CPU information """

    def __init__(self, core, hz, load):
        self._core = core
        self._hz = hz
        self._load = load

    def get_core(self):
        return self._core

    def get_hz(self):
        return self._hz

    def get_load(self):
        return self._load


def create_cpu_from_json(json_entry):
    return Cpu(json_entry['core'], json_entry['hz'], json_entry['load'])

""" Router memory information """


class Mem(object):
    """ Router memory information """

    def __init__(self, usage, total, hz, type):
        self._usage = usage
        self._total = total
        self._hz = hz
        self._type = type

    def get_usage(self):
        return self._usage

    def get_total(self):
        return self._total

    def get_hz(self):
        return self._hz

    def get_type(self):
        return self._type


def create_mem_from_json(json_entry):
    return Mem(json_entry['usage'], json_entry['total'], json_entry['hz'],
               json_entry['type'])

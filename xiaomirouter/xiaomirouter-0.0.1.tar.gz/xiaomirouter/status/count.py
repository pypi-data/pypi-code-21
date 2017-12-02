""" Client count information """


class Count(object):
    """ Client count """

    def __init__(self, all, online):
        self._all = all
        self._online = online

    def get_all(self):
        return self._all

    def get_online(self):
        return self._online


def create_count_from_json(json_entry):
    return Count(json_entry['all'], json_entry['online'])

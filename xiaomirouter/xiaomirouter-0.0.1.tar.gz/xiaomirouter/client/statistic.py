""" Connected client statistics """


class Statistics(object):
    """ A connected client statistics """

    def __init__(self, downspeed, online, upspeed):
        self._downspeed = downspeed
        self._online = online
        self._upspeed = upspeed

    def get_downspeed(self):
        return self._downspeed

    def get_online(self):
        return self._online

    def get_upspeed(self):
        return self._upspeed


def create_statistic_from_json(json_entry):
    # json_entry = json.loads(json_entry_as_string)
    return Statistics(json_entry['downspeed'], json_entry['online'],
                      json_entry['upspeed'])

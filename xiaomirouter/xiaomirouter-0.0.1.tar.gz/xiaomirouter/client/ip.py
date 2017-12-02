""" Ip Info """


class Ip(object):
    """ Ip Info """

    def __init__(self, downspeed, online, upspeed, active, ip):
        self._downspeed = downspeed
        self._online = online
        self._upspeed = upspeed
        self._active = active
        self._ip = ip

    def get_downspeed(self):
        return self._downspeed

    def get_online(self):
        return self._online

    def get_upspeed(self):
        return self._upspeed

    def get_active(self):
        return self._active

    def get_ip(self):
        return self._ip


def create_ip_from_json(json_entry):
    # json_entry = json.loads(json_entry_as_string)
    return Ip(json_entry['downspeed'], json_entry['online'],
              json_entry['upspeed'], json_entry['active'], json_entry['ip'])

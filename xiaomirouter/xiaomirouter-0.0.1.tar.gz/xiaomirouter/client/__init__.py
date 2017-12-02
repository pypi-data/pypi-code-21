""" Connected client """

from xiaomirouter.client.authority import create_authority_from_json
from xiaomirouter.client.ip import create_ip_from_json
from xiaomirouter.client.statistic import create_statistic_from_json


class Client(object):
    """ A connected client """

    def __init__(self, mac, oname, isap, parent, authority, push, online, name,
                 times, ips, statistics, type):
        self._mac = mac
        self._oname = oname
        self._isap = isap
        self._parent = parent
        self._authority = authority
        self._push = push
        self._online = online
        self._name = name
        self._times = times
        self._ips = ips
        self._statistics = statistics
        self._type = type

    def get_mac(self):
        return self._mac

    def get_original_name(self):
        return self._oname

    def get_isap(self):
        return self._isap

    def get_parent(self):
        return self._parent

    def get_authority(self):
        return self._authority

    def get_push(self):
        return self._push

    def get_online(self):
        return self._online

    def get_name(self):
        return self._name

    def get_times(self):
        return self._times

    def get_ips(self):
        return self._ips

    def get_statistics(self):
        return self._statistics

    def get_type(self):
        return self._type


def create_client_from_json(json_entry):
    # json_entry = json.loads(json_entry_as_string)
    ips = []
    for ip in json_entry['ip']:
        ips.append(create_ip_from_json(ip))
    statistics = create_statistic_from_json(json_entry['statistics'])
    authority = create_authority_from_json(json_entry['authority'])
    return Client(json_entry['mac'], json_entry['oname'], json_entry['isap'],
                  json_entry['parent'], authority,
                  json_entry['push'], json_entry['online'], json_entry['name'],
                  json_entry['times'], ips,
                  statistics, json_entry['type'])

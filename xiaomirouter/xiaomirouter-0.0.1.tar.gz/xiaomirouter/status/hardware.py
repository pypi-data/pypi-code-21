""" Router Hardware information """


class Hardware(object):
    """ Router hardware """

    def __init__(self, mac, platform, version, channel, sn):
        self._mac = mac
        self._platform = platform
        self._version = version
        self._channel = channel
        self._sn = sn

    def get_mac(self):
        return self._mac

    def get_platform(self):
        return self._platform

    def get_version(self):
        return self._version

    def get_channel(self):
        return self._channel

    def get_sn(self):
        return self._sn


def create_hardware_from_json(json_entry):
    return Hardware(json_entry['mac'], json_entry['platform'],
                    json_entry['version'], json_entry['channel'],
                    json_entry['sn'])

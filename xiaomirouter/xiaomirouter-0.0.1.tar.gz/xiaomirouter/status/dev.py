""" Router Hardware information """


class Dev(object):
    """ Router hardware """

    def __init__(self, mac, maxdownloadspeed, upload, upspeed, downspeed,
                 online, devname, maxuploadspeed, download):
        self._mac = mac
        self._maxdownloadspeed = maxdownloadspeed
        self._upload = upload
        self._upspeed = upspeed
        self._downspeed = downspeed
        self._online = online
        self._devname = devname
        self._maxuploadspeed = maxuploadspeed
        self._download = download

    def get_mac(self):
        return self._mac

    def get_maxdownloadspeed(self):
        return self._maxdownloadspeed

    def get_upload(self):
        return self._upload

    def get_upspeed(self):
        return self._upspeed

    def get_downspeed(self):
        return self._downspeed

    def get_online(self):
        return self._online

    def get_devname(self):
        return self._devname

    def get_maxuploadspeed(self):
        return self._maxuploadspeed

    def get_download(self):
        return self._download


def create_dev_from_json(json_entry):
    return Dev(json_entry['mac'], json_entry['maxdownloadspeed'],
               json_entry['upload'], json_entry['upspeed'],
               json_entry['downspeed'], json_entry['online'],
               json_entry['devname'], json_entry['maxuploadspeed'],
               json_entry['download'])

""" Router WAN information """


class Wan(object):
    """ WAN information"""

    def __init__(self, downspeed, maxdownloadspeed, history, devname, upload,
                 upspeed, maxuploadspeed, download):
        self._downspeed = downspeed
        self._maxdownloadspeed = maxdownloadspeed
        self._history = history
        self._devname = devname
        self._upload = upload
        self._upspeed = upspeed
        self._maxuploadspeed = maxuploadspeed
        self._download = download

    def get_downspeed(self):
        return self._downspeed

    def get_maxdownloadspeed(self):
        return self._maxdownloadspeed

    def get_history(self):
        return self._history

    def get_devname(self):
        return self._devname

    def get_upload(self):
        return self._upload

    def get_upspeed(self):
        return self._upspeed

    def get_maxuploadspeed(self):
        return self._maxuploadspeed

    def get_download(self):
        return self._download


def create_wan_from_json(json_entry):
    return Wan(json_entry['downspeed'], json_entry['maxdownloadspeed'],
               json_entry['history'], json_entry['devname'],
               json_entry['upload'], json_entry['upspeed'],
               json_entry['maxuploadspeed'], json_entry['download'])

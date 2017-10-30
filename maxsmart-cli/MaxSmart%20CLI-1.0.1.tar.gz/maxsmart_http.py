import json
import requests

class MaxsmartHttp(object):
    @staticmethod
    def send(device, command, params = {}):
        params['sn'] = device.sn
        options = json.dumps(params)

        return requests.get('http://%s?cmd=%d' % (device.ip, command),
                            params={'json': options})

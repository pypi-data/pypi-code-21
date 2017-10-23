import socket

from zeroconf import ServiceInfo, Zeroconf


def _get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('6.6.6.6', 1))  # udp does not send packets on connect
        ip = s.getsockname()[0]
    except:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


class Advertiser(object):
    def __init__(self, accessory):
        self.info = self._info_for_accessory(accessory)
        self.zeroconf = Zeroconf()

    def get_txt_from_accessory(self, accessory):
        return {
            'md': accessory.name,
            'pv': '1.0',
            'id': accessory.id,
            'c#': accessory.config,
            'ff': '0',
            'ci': accessory.category,
            'sf': accessory.paired,
            's#': accessory.state,
        }

    def _info_for_accessory(self, accessory):
        txt = self.get_txt_from_accessory(accessory)
        info = ServiceInfo(
            '_hap._tcp.local.',
            '{name}._hap._tcp.local.'.format(name=accessory.name),
            address=socket.inet_aton(_get_ip()),
            port=52123,
            properties=txt,
            server='lcarvalh-mn1.local.', #socket.getfqdn(),
        )

        return info

    def start_advertising(self):
        self.zeroconf.register_service(self.info)

    def stop_advertising(self):
        self.zeroconf.unregister_service(self.info)

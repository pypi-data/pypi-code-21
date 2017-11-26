import socket
import netifaces
from zeroconf import (
    ServiceBrowser, ServiceInfo, ServiceStateChange, Zeroconf
)

import logging
logger = logging.getLogger(__name__)

service_type = '_pandoraclient._tcp.local.'

def get_broadcast_interfaces():
    return list(set(
        addr['addr']
        for iface in netifaces.interfaces()
        for addr in netifaces.ifaddresses(iface).get(socket.AF_INET, [])
        if addr.get('netmask') != '255.255.255.255' and addr.get('broadcast')
    ))


class Server(object):
    local_info = None
    local_ips = None

    def __init__(self, port):
        self.port = port
        self.name = socket.gethostname().partition('.')[0] + '-%s' % port
        self.local_ips = get_broadcast_interfaces()
        self.zeroconf = {ip: Zeroconf(interfaces=[ip]) for ip in self.local_ips}
        self.register_service()

    def register_service(self):
        if self.local_info:
            for local_ip, local_info in self.local_info:
                self.zeroconf[local_ip].unregister_service(local_info)
            self.local_info = None

        local_name = socket.gethostname().partition('.')[0] + '.local.'
        port = self.port
        desc = {}
        self.local_info = []
        for i, local_ip in enumerate(get_broadcast_interfaces()):
            if i:
                name = '%s-%s.%s' % (self.name, i+1, service_type)
            else:
                name = '%s.%s' % (self.name, service_type)
            local_info = ServiceInfo(service_type, name,
                                     socket.inet_aton(local_ip), port, 0, 0, desc, local_name)
            self.zeroconf[local_ip].register_service(local_info)
            self.local_info.append((local_ip, local_info))

    def __del__(self):
        self.close()

    def close(self):
        if self.local_info:
            for local_ip, local_info in self.local_info:
                try:
                    self.zeroconf[local_ip].unregister_service(local_info)
                except:
                    logger.debug('exception closing zeroconf', exc_info=True)
            self.local_info = None
        if self.zeroconf:
            for local_ip in self.zeroconf:
                try:
                    self.zeroconf[local_ip].close()
                except:
                    logger.debug('exception closing zeroconf', exc_info=True)
            self.zeroconf = None

class LocalNodes(dict):

    def __init__(self):
        self.local_ips = get_broadcast_interfaces()
        self.zeroconf = {ip: Zeroconf(interfaces=[ip]) for ip in self.local_ips}
        self.browse()

    def browse(self):
        self.browser = {
            ip: ServiceBrowser(self.zeroconf[ip], service_type, handlers=[self.on_service_state_change])
            for ip in self.zeroconf
        }

    def __del__(self):
        self.close()

    def close(self):
        if self.zeroconf:
            for local_ip in self.zeroconf:
                try:
                    self.zeroconf[local_ip].close()
                except:
                    logger.debug('exception closing zeroconf', exc_info=True)
            self.zeroconf = None
        for id in list(self):
            self.pop(id, None)

    def on_service_state_change(self, zeroconf, service_type, name, state_change):
        id = name.split('.')[0].split('-')[0]
        if state_change is ServiceStateChange.Added:
            info = zeroconf.get_service_info(service_type, name)
            if info:
                self[id] = 'http://%s:%s' % (socket.inet_ntoa(info.address), info.port)
        elif state_change is ServiceStateChange.Removed:
            logger.debug('remove: %s', id)
            self.pop(id, None)


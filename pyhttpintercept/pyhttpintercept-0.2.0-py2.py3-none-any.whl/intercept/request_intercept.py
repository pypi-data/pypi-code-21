
import os
import sys
import time
import logging_helper
from networkutil.device_config import Devices
from pyhttpintercept import (ThreadedHTTPWebServer,
                             HTTPWebServer,
                             HTTPRequestHandler,
                             HTTPRequestHandlerWithProfiling)
from networkutil.endpoint_config import Endpoints
from pydnserver import dns_lookup, DNSServer

logging = logging_helper.setup_logging()


class RequestIntercept(object):

    def __init__(self):

        self.active_devices = None

        self.http_ports = [80, ]
        self.dns_port = 53

        self.http_server_instances = {}
        self.dns_servers = {}

    def start(self,
              threaded=True,
              profiling=False):

        try:
            if sys.platform == u'darwin' and os.geteuid() != 0:
                raise Exception(u'You are running macOS please restart with sudo!')

            logging.info(u'Starting up, use <Ctrl-C> to stop!')

            self.active_devices = Devices().get_active_items()
            logging.debug(self.active_devices)

            active_redirections = dns_lookup.get_active_redirection_config()

            # TODO: Using .values, but might be nice to make Endpoints iterable.
            for endpoint in Endpoints():
                temp_port = int(endpoint.port)

                if temp_port not in self.http_ports:
                    if endpoint.hostname in active_redirections:
                        self.http_ports.append(temp_port)

            # TODO: Go through redirection to pull active redirection sources
            #       Go through endpoints that match the redirect hostname
            #       and any that are for ports not in the
            #       self.http_ports list, add it.
            #

            for http_port in self.http_ports:
                server_address = (u'', http_port)
                # Start HTTP Server

                server_class = (ThreadedHTTPWebServer
                                if threaded
                                else HTTPWebServer)

                request_handler_class = (HTTPRequestHandlerWithProfiling
                                         if profiling
                                         else HTTPRequestHandler)

                self.http_server_instances[http_port] = server_class(server_address=server_address,
                                                                     request_handler_class=request_handler_class)

                self.http_server_instances[http_port].start()

                time.sleep(1)

            # Start DNS Servers for devices
            for device in self.active_devices:
                logging.debug(device.name)

                dns_ip = device.dns  # TODO: This relies on device config having dns. May not be true

                if dns_ip not in self.dns_servers:

                    self.dns_servers[dns_ip] = DNSServer(interface=dns_ip,
                                                         port=self.dns_port)
                    self.dns_servers[dns_ip].start()
                    time.sleep(1)

            self.post_start_tasks()

            logging.info(u'Ready...')

        except Exception as err:
            logging.exception(err)
            logging.fatal(u'Unexpected Exception.')

    def stop(self):

        # Reset STB DNS server
        if self.active_devices:
            for device in self.active_devices:

                dns_ip = device.dns

                # Shutdown DNS Server
                if self.dns_servers.get(dns_ip):
                    if self.dns_servers[dns_ip].active:
                        self.dns_servers[dns_ip].stop()
                        del self.dns_servers[dns_ip]

        # Shutdown HTTP Server
        for http_server in self.http_server_instances.values():
            if http_server.active:
                http_server.stop()

        logging.info(u'Shut Down Complete')

    def reload_config(self):
        for http_server_instance in self.http_server_instances.values():
            http_server_instance.scenarios.reload_active_scenario()

    def post_start_tasks(self):
        pass
        # override to performs tasks after the servers have started


if __name__ == u'__main__':

    ri = RequestIntercept()

    try:
        ri.start()

        logging.debug(u'READY')

        while True:
            pass

    except KeyboardInterrupt:
        ri.stop()

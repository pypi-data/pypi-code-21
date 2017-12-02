""" XiaomiRouter

http://www.xiaomi.com
"""

import logging
import threading
import time

import requests

from xiaomirouter.client import Client, create_client_from_json
from xiaomirouter.status import create_status_from_json

ROUTER_ADMINISTRATOR = 'admin'
TIMEOUT = 5
RECONNECT_TIME = 5

_LOGGER = logging.getLogger(__name__)


class XiaomiRouter(object):
    """ Represents a xiaomi router. """

    def __init__(self, host, password, username=ROUTER_ADMINISTRATOR):
        self._host = host
        self._password = password
        self._username = username
        self._success_init = self._init_token()
        keep_alive_thread = threading.Thread(target=self._keep_alive())
        keep_alive_thread.daemon = True
        keep_alive_thread.start()

    def retrieve_client_list(self):
        """Get the device list."""
        device_list \
            = self._retrieve_json_from_endpoint('api/misystem/devicelist')
        if device_list is None:
            return
        clients = []
        for device_entry in device_list['list']:
            clients.append(create_client_from_json(device_entry))
        return clients

    def retrieve_status_info(self):
        """Get the device status."""
        json_status_info \
            = self._retrieve_json_from_endpoint('api/misystem/status')
        # http://192.168.0.1/cgi-bin/luci/;stok=1234/api/misystem/status
        return create_status_from_json(json_status_info)

    def is_successfully_initialised(self):
        return self._success_init

    def reconnect(self):
        if self._init_token():
            return
        time.sleep(RECONNECT_TIME)

    def _keep_alive(self):
        if not self._success_init:
            self.reconnect()

    def _init_token(self):
        """Get authentication token for the given host+username+password."""
        url = 'http://{}/cgi-bin/luci/api/xqsystem/login'.format(self._host)
        data = {'username': self._username, 'password': self._password}
        try:
            res = requests.post(url, data=data, timeout=5)
        except requests.exceptions.Timeout:
            _LOGGER.exception("Connection to the mi router timed out")
            return False
        if res.status_code == 200:
            try:
                result = res.json()
            except ValueError:
                # If JSON decoder could not parse the response
                _LOGGER.exception("Failed to parse response from mi router")
                return False
            try:
                self._token = result['token']
                return True
            except KeyError:
                error_message = "Mi router token cannot be refreshed, " \
                                + "response from url: [%s] \nwith parameter: " \
                                + "[%s] \nwas: [%s]"
                _LOGGER.exception(error_message, url, data, result)
                return False
        else:
            _LOGGER.error(
                'Invalid response: [%s] at url: [%s] with data [%s]',
                res, url, data)
            return False

    def _retrieve_json_from_endpoint(self, endpoint, **kwargs):
        if not self._success_init:
            return
        url = "http://{}/cgi-bin/luci/;stok={}/{}"
        url = url.format(self._host, self._token, endpoint)
        try:
            res = requests.get(url, timeout=TIMEOUT, **kwargs)
        except requests.exceptions.Timeout:
            _LOGGER.exception(
                "Connection to the router timed out at URL %s", url)
            self._success_init = False
            return
        if res.status_code != 200:
            _LOGGER.exception(
                "Connection failed with http code %s", res.status_code)
            self._success_init = False
            return
        try:
            result = res.json()
        except ValueError:
            # If json decoder could not parse the response
            _LOGGER.exception("Failed to parse response from mi router")
            return
        try:
            xiaomi_code = result['code']
        except KeyError:
            _LOGGER.exception(
                "No field code in response from mi router. %s", result)
            return
        if xiaomi_code == 0:
            return result
        else:
            _LOGGER.info(
                "Receive wrong Xiaomi code %s, expected 0 in response %s",
                xiaomi_code, result)
            return

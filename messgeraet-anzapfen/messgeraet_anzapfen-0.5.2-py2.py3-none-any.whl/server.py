"""
    COPYRIGHT (C) 2017 by Sebastian Stigler

    NAME
        server.py -- Component which sends the result to the logging server

    FIRST RELEASE
        2017-07-05  Sebastian Stigler  sebastian.stigler@hs-aalen.de

"""
import json
import logging

import requests

from urllib.parse import urljoin

from messgeraet_anzapfen.configurable import Configurable
from messgeraet_anzapfen.serial import hashserial
from messgeraet_anzapfen.verify import verify_sensor_id

_logger = logging.getLogger(__name__)

__all__ = ['Server', 'ServerError']


class ServerError(Exception):
    """Problems while sending"""


class Server(Configurable):
    """Sends the result to the logging server"""

    config_keys = ['url', 'sensor_id']

    def send(self, data, sending, token):
        """send data to the logging server"""
        url = urljoin(self.config.get('url'),
                      self.config.get('endpoint', 'sensor'))
        header = {'Authorization': 'Bearer ' + token}
        send_data = {'sensor': self.config.get('sensor_id'),
                     #'value': json.dumps(data),
                     'value': data,
                     'hwid': hashserial()}
        if sending:
            try:
                verify_sensor_id(send_data['sensor'])
                _logger.info('Sending data from sensor %s to %s.' %
                             (self.config.get('sensor_id'), url))
                res = requests.post(url, json=send_data, headers=header,
                                    timeout=10)
                res.raise_for_status()
                _logger.info("Post of sensor data successfully.")
                _logger.debug("Result text of postrequest: %s" % res.text)
            except ValueError as err:
                _logger.error('Value Error: %s' % err)
                raise ServerError('Value Error: %s' % err) from err
            except requests.exceptions.HTTPError as err:
                _logger.debug('HTTP errormessage: {msg}'.format(msg=res.text))
                raise ServerError("HTTPError: %s" % err) from err
            except requests.exceptions.RequestException as err:
                raise ServerError("RequestError") from err
        else:
            print(json.dumps(send_data, indent=2))

# vim: ft=python ts=4 sta sw=4 et ai
# python: 3

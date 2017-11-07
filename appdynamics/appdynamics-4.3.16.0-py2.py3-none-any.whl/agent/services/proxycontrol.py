# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Services for controlling the proxy once it is running.

This module contains the definition of the `ProxyControlService` and the
mapper for turning the agent's configuration into a `StartNodeRequest`.

"""

from __future__ import unicode_literals
import logging
import threading

from appdynamics import get_reported_version
from appdynamics import config
from appdynamics.agent.core.transport import ControlTransport


class ProxyControlService(threading.Thread):
    def __init__(self, response_callback):
        super(ProxyControlService, self).__init__()
        self.name = 'ProxyControlService'
        self.response_callback = response_callback
        self.connect_event = threading.Event()
        self.connect_event.set()
        self.running = False
        self.logger = logging.getLogger('appdynamics.agent')
        self.retry_delay = None
        self.daemon = True
        self.started_event = threading.Event()

    def reconnect(self):
        self.connect_event.set()

    def run(self):
        transport = ControlTransport()
        self.running = True

        while self._is_running():
            self.connect_event.wait()

            self._connect(transport)
            self._send_start_node_request(transport)
            self._handle_start_node_response(transport)

            self.connect_event.clear()

    def _connect(self, transport):
        # Disconnect first, just in case we are reconnecting.
        transport.disconnect()
        transport.connect('ipc://%s/0' % config.PROXY_CONTROL_PATH)

    def _send_start_node_request(self, transport):
        self.started_event.clear()
        request = make_start_node_request_dict()
        transport.send(request)
        self.logger.info('Sent start node request:\n%r', request)

    def _handle_start_node_response(self, transport):
        # Wait for a response.  If we don't get one, retry after a delay.
        response = transport.recv(timeout_ms=config.PROXY_STARTUP_READ_TIMEOUT_MS)

        if response:
            self.logger.info('Got start node response:\n%s', response)
            self.response_callback(response)
            self.started_event.set()
        else:
            if self.retry_delay is None:
                self.retry_delay = config.PROXY_STARTUP_INITIAL_RETRY_DELAY_MS
            else:
                self.retry_delay = min(config.PROXY_STARTUP_MAX_RETRY_DELAY_MS, self.retry_delay * 2)

            self.logger.error('No response to start node request: reconnecting in %dms', self.retry_delay)
            threading.Timer(self.retry_delay / 1000., self.reconnect).start()

    def wait_for_start(self, timeout_ms=None):
        if timeout_ms is not None:
            self.started_event.wait(timeout_ms / 1000.)
        else:
            self.started_event.wait()

    def _is_running(self):
        return self.running


def make_start_node_request_dict():
    """Make a start node request from agent configuration.

    The agent configuration comes from environment variables. See
    :py:mod:`appdynamics.config`.

    """
    ssl_enabled = bool(config.SSL_ENABLED)
    controller_port = config.CONTROLLER_PORT or (443 if ssl_enabled else 80)

    return {
        'appName': config.APP_NAME,
        'tierName': config.TIER_NAME,
        'nodeName': config.NODE_NAME,
        'controllerHost': config.CONTROLLER_HOST,
        'controllerPort': int(controller_port),
        'sslEnabled': ssl_enabled,
        'logsDir': config.LOGS_DIR,
        'accountName': config.ACCOUNT_NAME,
        'accountAccessKey': config.ACCOUNT_ACCESS_KEY,
        'httpProxyHost': config.HTTP_PROXY_HOST,
        'httpProxyPort': config.HTTP_PROXY_PORT,
        'httpProxyUser': config.HTTP_PROXY_USER,
        'httpProxyPasswordFile': config.HTTP_PROXY_PASSWORD_FILE,
        'agentVersion': get_reported_version(),
    }

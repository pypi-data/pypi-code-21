# coding=utf-8
###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Andy Grabow, VFK AG
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

# we refuse to run under python 2
import sys
if sys.version_info[0] < 3:
    print("Your Python version: " + sys.version)
    raise Exception("The Twisted client is only intended to run under Python 3.x")


import json
import logging
import re
from hashlib import md5
from copy import deepcopy

from datetime import datetime
from twisted.internet.protocol import ReconnectingClientFactory
from autobahn.twisted.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
log = logging.getLogger("msb_client")
log.addHandler(handler)
log.setLevel(logging.DEBUG)


class MSBClientException(Exception):
    pass

MSB_MESSAGE_TYPES = [
    'IO',
    'NIO',
    'IO_CONNECTED',
    'IO_REGISTERED',
    'IO_PUBLISHED',
    'NIO_ALREADY_CONNECTED',
    'NIO_REGISTRATION_ERROR',
    'NIO_UNEXPECTED_REGISTRATION_ERROR',
    'NIO_EVENT_FORWARDING_ERROR',
    'NIO_UNEXPECTED_EVENT_FORWARDING_ERROR',
]


class MSBClientProtocol(WebSocketClientProtocol):
    events = {}
    functions = {}
    autoPingInterval = 10

    def on_init(self):
        # print('did something ..')
        pass

    def on_connection_lost(self):
        # do something when the connection drops
        pass

    def onConnect(self, response):
        log.info("Server connected: {0}".format(response.peer))
        self.factory.resetDelay()

        registration = "R " + json.dumps(self.get_self_description())
        self.sendMessage(bytes(registration, 'utf8'))

    def onOpen(self):
        log.info("WebSocket connection open.")

    def onMessage(self, payload, is_binary):
        if is_binary:
            raise MSBClientException('binary messages are not excepted')

        message = payload.decode('utf8')
        if message in MSB_MESSAGE_TYPES:
            log.info('MSB: {}'.format(message))

            if message == "IO_REGISTERED":
                # once connected do whatever was requested by the client
                self.on_init()

            if message.startswith('NIO'):
                log.error('something is wrong .. retrying ..')
                self.sendClose()
        else:
            # callback message
            if message.startswith('C '):
                log.info('Callback received: {}'.format(message))
                message = json.loads(message[2:])
                if self.functions[message['functionId']]:
                    callback = self.functions[message['functionId']]['implementation']
                    parameters = message['functionParameters']
                    if type(parameters) == list:
                        parameters = parameters[0]['value']
                    callback(**parameters)
            else:
                log.info(message)

    def onClose(self, was_clean, code, reason):
        log.info("WebSocket connection closed: {0}".format(reason))

    def get_self_description(self):

        events = []
        functions = []

        for k, v in deepcopy(self.events).items():
            v.pop('implementation', None)
            events.append(v)
        for k, v in deepcopy(self.functions).items():
            v.pop('implementation', None)
            functions.append(v)

        self_description = {
            'uuid': self.config['uuid'],
            'name': self.config['name'],
            'description': self.config['description'],
            'token': self.config['token'],
            '@class': self.config['class'],
            'events': events,
            'functions': functions,
        }

        return self_description

    def send_event(self, event_id, **kwargs):
        if event_id in self.events:
            log.info('sending something ..')
            event = self.events[event_id]['implementation']
            event['postDate'] = datetime.now().isoformat()

            # prepare event
            for k, v in kwargs.items():
                val = v.decode('utf-8') if type(v) == bytes else v
                event['dataObject'][k] = val

            message = "E " + json.dumps(event)
            self.sendMessage(bytes(message, 'utf8'))


class MSBClientFactory(WebSocketClientFactory, ReconnectingClientFactory):
    maxDelay = 300

    def __init__(self, *args, **kwargs):
        if 'config' not in kwargs:
            raise MSBClientException('no config provided')

        self.protocol = kwargs.pop('protocol', MSBClientProtocol)
        self.protocol.config = kwargs.pop('config')
        self.debug = kwargs.pop('debug', False)
        self.broker_url = args[0]

        super(MSBClientFactory, self).__init__(*args, **kwargs)

    def get_domain(self):
        domain = re.sub(r'.*://', '', self.broker_url)
        domain = re.sub(r'/.*', '', domain)
        domain = re.sub(r':.*', '', domain)
        return domain

    def clientConnectionLost(self, connector, reason):
        print('Lost connection.  Reason:', reason)
        self.retry(connector)
        print('retrying in: ', self.delay)

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed. Reason:', reason)
        self.retry(connector)
        print('retrying in: ', self.delay)

    def add_function(self, function_dict):
        ids = []
        for event_id in function_dict.get("responseEvents", []):
            if event_id in self.protocol.events:
                ids.append(self.protocol.events[event_id]['@id'])
        function_dict['responseEvents'] = ids

        function_dict['functionId'] = "/" + function_dict['functionId']
        self.protocol.functions[function_dict['functionId']] = function_dict

    def add_event(self, event_dict):
        orig_event_id = event_dict.get('eventId')
        event_id = orig_event_id or str(len(self.protocol.events) + 1) if self.debug else md5(
            str(event_dict).encode()).hexdigest()
        event_dict['eventId'] = event_id
        event_dict["@id"] = len(self.protocol.events) + 1
        event_dict['implementation']['uuid'] = self.protocol.config['uuid']
        event_dict['implementation']['eventId'] = event_id
        self.protocol.events[orig_event_id] = event_dict

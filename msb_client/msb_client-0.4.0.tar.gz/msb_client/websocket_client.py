# coding=utf-8
import json
import logging
from copy import deepcopy
from hashlib import md5

from datetime import datetime
from ws4py.client.threadedclient import WebSocketClient

log = logging.getLogger("msb_client")
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)
log.setLevel(logging.DEBUG)


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
    'NIO_UNEXPECTED_EVENT_FORWARDING_ERROR'
]


class MSBClientException(Exception):
    pass


class MSBClient(WebSocketClient):

    def __init__(self, url, config=None, debug=False, *args, **kwargs):

        if not config:
            raise MSBClientException('no config provided')

        self.config = config
        self.debug = debug

        self.events = {}
        self.functions = {}

        kwargs['heartbeat_freq'] = 2.0

        super(MSBClient, self).__init__(url, *args, **kwargs)

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

    def do_something(self):
        """ overwrite this method to execute some code after registering with the MSB """
        pass

    def opened(self):

        registration = "R " + json.dumps(self.get_self_description())
        self.send(registration)

        self.do_something()

    def closed(self, code, reason=None):
        log.info("Connection closed")

    def received_message(self, msg):
        message = str(msg)
        if message in MSB_MESSAGE_TYPES:
            log.info('MSB: {}'.format(message))
        else:

            # callback message
            if message.startswith('C '):
                message = json.loads(message[2:])
                if self.functions[message['functionId']]:
                    callback = self.functions[message['functionId']]['implementation']
                    parameters = message['functionParameters'][0]['value']
                    callback(**parameters)
            else:
                log.info(message)

    def add_function(self, function_dict):
        ids = []
        for event_id in function_dict.get("responseEvents", []):
            if event_id in self.events:
                ids.append(self.events[event_id]['@id'])
        function_dict['responseEvents'] = ids

        function_dict['functionId'] = "/" + function_dict['functionId']
        self.functions[function_dict['functionId']] = function_dict

    def add_event(self, event_dict):
        orig_event_id = event_dict.get('eventId')
        event_id = orig_event_id or str(len(self.events) + 1) if self.debug else md5(str(event_dict).encode()).hexdigest()
        event_dict['eventId'] = event_id
        event_dict["@id"] = len(self.events) + 1
        event_dict['implementation']['uuid'] = self.config['uuid']
        event_dict['implementation']['eventId'] = event_id
        self.events[orig_event_id] = event_dict

    def send_event(self, event_id, **kwargs):
        if event_id in self.events:
            log.info('sending something ..')
            event = self.events[event_id]['implementation']
            event['postDate'] = datetime.now().isoformat()

            # prepare event
            for k, v in kwargs.items():
                event['dataObject'][k] = v

            message = "E " + json.dumps(event)
            self.send(message)

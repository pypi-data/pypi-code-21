import logging

class MissingInfoException(Exception):
    pass

class Handler(object):
    def __init__(self, manager):
        self.manager = manager
        self.sender = None

        self.last_ping_id = None

    def set_sender(self, sender):
        self.sender = sender

    def handle(self, message):
        payload = message.header

        if 'type' not in payload:
            logging.warning("Ignored because no type")
            return None

        payload_type = payload['type']
        payload.pop('type')

        self.manager.forward(payload_type, payload)

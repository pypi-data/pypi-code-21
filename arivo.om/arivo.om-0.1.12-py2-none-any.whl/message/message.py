import json

import time


class Topic(object):
    MEDIUM = "medium"  # alpr, nfc, command
    ACCESS_ACCEPT = "access_accept"  # open
    ACCESS_REJECT = "access_reject"  # e.g. if number plate is not found in database
    SENSOR = "sensor"  # induction loop e.g for presence or counting
    COUNT = "count"  # topic for the actual count how many vehicles are e.g. in the parking lot


class Message(dict):
    _MANDATORY_FIELDS = ["name", "type"]

    @classmethod
    def parse(cls, msg):
        try:
            parsed = json.loads(msg.encode())
        except Exception as e:
            raise ValueError("Could not parse message")
        if not all(k in parsed for k in cls._MANDATORY_FIELDS):
            raise KeyError("Mandatory keys not found in message")
        return parsed

    @classmethod
    def serialize(cls, msg):
        if not isinstance(msg, dict):
            raise TypeError("Message is not of type dict")
        if not all(k in msg for k in cls._MANDATORY_FIELDS):
            raise KeyError("Mandatory keys not found in message")
        try:
            msg.update(timestamp=time.time())
            if "_" not in msg["name"]:
                msg.update(name="{}_{}".format(msg["type"], msg["name"]))
            serialized = json.dumps(msg)
        except (TypeError, ValueError):
            raise ValueError("Could not serialize message")
        return serialized

    def __init__(self, name=None, type=None, *args, **kwargs):
        if name is not None and type is not None:
            kwargs["name"] = name
            kwargs["type"] = type
        super(Message, self).__init__(*args, **kwargs)

    def to_json(self):
        return Message.serialize(self)

    def from_json(self, serialized):
        self.clear()
        self.update(Message.parse(serialized))

    def to_socket(self, sock, topic):
        sock.send_multipart((topic, self.to_json()))

    def from_socket(self, sock):
        topic, payload = sock.recv_multipart()
        self.from_json(payload)
        return topic

    def set_gateway(self, gate, direction=None):
        gateway = dict(gate=(str(gate) or "unknown").lower(),
                       direction=(str(direction) or "").lower())
        self.update(gateway=gateway)

    def is_gateway(self):
        return "gateway" in self

    def __str__(self):
        return self.to_json()

    def __repr__(self):
        return str(self)

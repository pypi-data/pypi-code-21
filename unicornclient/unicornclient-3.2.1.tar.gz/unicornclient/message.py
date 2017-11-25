import json

class Message(object):
    def __init__(self, payload=None):
        self.header = {}
        if isinstance(payload, dict):
            self.header = payload
        self.body = b''

    def set_header(self, header):
        self.header = header

    def set_body(self, body):
        self.body = body

    def encode(self):
        header_serialized = json.dumps(_clean_dict(self.header))
        header_size = len(header_serialized.encode())
        body = b''
        body_size = 0

        if self.body:
            body = self.body
            body_size = len(body)

        message_start = str(header_size) + ',' + str(body_size) + ':'
        message_encoded = message_start.encode() + header_serialized.encode()
        if body_size > 0:
            message_encoded += body

        return message_encoded


def _clean_dict(data):
    if not isinstance(data, dict):
        return data

    new_dict = {}
    for key in data.keys():
        value = data[key]
        if value is not None:
            new_dict[key] = _clean_dict(value)

    return new_dict

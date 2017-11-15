from enum import Enum
from struct import pack, unpack, calcsize
from hashlib import sha256


class WebSocketPacketType(Enum):
    join = 0
    leave = 1
    publish = 2


class _WebSocketPacket(object):

    def __init__(self):
        # 16 bits for type
        # 2 bytes padding
        # 32 bytes for hashed topic
        # 4 bytes for payload length
        self._header = '<h2x32sI'
        self._header_size = calcsize(self._header)

    @staticmethod
    def hash(topic):
        btopic = topic.encode()
        hashed_obj = sha256(btopic)
        hashed = hashed_obj.digest()
        return hashed

    def pack(self, _type, topic, payload=None):
        if payload:
            payload_len = len(payload)
        else:
            payload_len = 0

        hashed_topic = self.hash(topic)
        buffer = pack(self._header, _type.value, hashed_topic, payload_len)
        if payload_len:
            buffer += pack("{}s".format(payload_len), payload)

        return buffer

    def unpack(self, data):
        _type, topic, payload_len = \
            unpack(self._header, data[:self._header_size])
        if payload_len:
            payload, = unpack('{}s'.format(payload_len),
                              data[self._header_size:])
        else:
            payload = None
        return _type, topic, payload


WebSocketPacket = _WebSocketPacket()

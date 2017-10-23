import math
import base64


class Base64(object):

    def __init__(self, data):
        self.data = data
        self.byte_buffer = b''
        self.offset = 0

    def _read_bytes(self, length):
        start = self.offset

        full_buffer = self.byte_buffer

        if length > len(self.byte_buffer):
            self.offset = start + math.ceil((len(self.byte_buffer) - length) / 3) * 4

            raw = self.data[start:self.offset]

            full_buffer += base64.b64decode(raw)

        self.byte_buffer = full_buffer[length:]

        return full_buffer[:length]

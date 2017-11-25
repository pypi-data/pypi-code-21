import enum
import json
import logging

from . import message

class State(enum.Enum):
    HEADER_SIZE = 1
    BODY_SIZE = 2
    HEADER_DATA = 3
    BODY_DATA = 4
    DONE = 5

class Parser(object):
    def __init__(self):
        self.remaining = b''

        self.state = None
        self.buffer = b''
        self.message = None
        self.header_size = 0
        self.body_size = 0

        self.reset()

    def reset(self):
        self.state = State.HEADER_SIZE
        self.buffer = b''
        self.message = None
        self.header_size = 0
        self.body_size = 0

    def feed(self, data):
        self.remaining = self.remaining + data

    def parse(self):
        result = []
        max_iterations = 100
        iterations = 0
        while iterations < max_iterations:
            parsed = self.parse_one()
            if parsed:
                result.append(parsed)
            if not self.remaining:
                break
            iterations += 1
        return result

    def parse_one(self):
        data = self.remaining

        try:
            last_index = 0
            for index, byte_int in enumerate(data):
                byte = bytes([byte_int])
                last_index = index

                if self.state == State.HEADER_SIZE:
                    self.process_header_size(byte)
                elif self.state == State.BODY_SIZE:
                    self.process_body_size(byte)
                elif self.state == State.HEADER_DATA:
                    self.process_header_data(byte)
                elif self.state == State.BODY_DATA:
                    self.process_body_data(byte)
                elif self.state == State.DONE:
                    last_index -= 1
                    break

            self.remaining = data[last_index+1:]

            if self.state == State.DONE:
                result = self.message
                self.reset()
                return result
            return None

        except ValueError as err:
            logging.error('parser ValueError')
            logging.error(err, exc_info=True)
            self.reset()
            return None

    def process_header_size(self, byte):
        if byte == b',':
            self.header_size = int(self.buffer.decode())
            self.state = State.BODY_SIZE
            self.buffer = b''
        else:
            self.buffer += byte

    def process_body_size(self, byte):
        if byte == b':':
            self.body_size = int(self.buffer.decode())
            self.state = State.HEADER_DATA
            self.buffer = b''
        else:
            self.buffer += byte

    def process_header_data(self, byte):
        self.buffer += byte
        if len(self.buffer) == self.header_size:
            self.message = message.Message()
            header = self._decode_header(self.buffer.decode())
            self.message.set_header(header)
            self.state = State.BODY_DATA if self.body_size > 0 else State.DONE
            self.buffer = b''

    def process_body_data(self, byte):
        self.buffer += byte
        if len(self.buffer) == self.body_size:
            self.message.set_body(self.buffer)
            self.state = State.DONE
            self.buffer = b''

    def _decode_header(self, json_string):
        try:
            return json.loads(json_string)
        except ValueError as err:
            logging.warning('JSON decode error: ' + str(err))
            return None

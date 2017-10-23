import base64
import sys
import struct
import xml.etree.ElementTree as ET

import zlib

_order = ('<' if sys.byteorder == 'little' else '>')
_fmt = {
    'Float32': 'f',
    'Int64': 'q',
}


class DataArray(object):
    block_size = 32768

    def __init__(self):
        self.type = 'Float32'
        self.name = None
        self.num_components = None
        self.format = 'ascii'
        self.offset = None
        self.data = None

    def __len__(self):
        if self.num_components:
            return len(self.data) // self.num_components

        return len(self.data)

    def to_xml(self, **kwargs):
        el = ET.Element('DataArray')

        el.set('type', self.type)
        el.set('format', self.format)

        if self.name is not None:
            el.set('Name', self.name)

        if self.num_components is not None:
            el.set('NumberOfComponents', str(self.num_components))

        if self.format == 'appended':
            el.set('offset', str(self.offset))

        el.text = self._serialize_data(**kwargs)

        return el

    def _serialize_data(self, **kwargs):
        if self.format == 'ascii':
            return ' '.join(str(d) for d in self.data)

        if self.format == 'binary':
            if kwargs.get('compress'):
                return self._binary_compressed_data().decode()
            return self._binary_data().decode()

    def _binary_data(self):
        fmt = _order + str(len(self.data)) + _fmt[self.type]

        byte_array = struct.pack(fmt, *self.data)

        header = struct.pack(_order + 'I', len(byte_array))

        return base64.b64encode(header + byte_array)

    def _binary_compressed_data(self):
        fmt = _order + str(len(self.data)) + _fmt[self.type]
        byte_array = struct.pack(fmt, *self.data)

        partial_size = len(byte_array)

        # TODO: implement multi-block structure
        assert partial_size < self.block_size

        num_blocks = 1
        compressed_data1 = zlib.compress(byte_array)
        compressed_size1 = len(compressed_data1)

        header = struct.pack(_order + '4I', num_blocks, self.block_size, partial_size, compressed_size1)

        return base64.b64encode(header) + base64.b64encode(compressed_data1)
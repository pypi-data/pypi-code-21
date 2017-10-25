# -*- coding: utf-8 -*-
# Copyright (c) 2016-2018 Braintech Sp. z o.o. [Ltd.] <http://www.braintech.pl>
# All rights reserved.

"""
Module providing generic temporary data buffer.

Author:
     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
"""
from .data_raw_write_proxy import DataRawWriteProxy, SamplePacket

BUF_SIZE = 1024


class DataBufferedWriteProxy(DataRawWriteProxy):
    """Subclass of class 'DataRawWriteProxy', stores data in temp buffer."""

    def __init__(self, p_file_path, p_append_ts=False, p_sample_type='FLOAT'):
        """Open p_file_path file for writing."""
        super().__init__(p_file_path, p_append_ts, p_sample_type)
        self._buffer = b''

    def data_received(self, packet: SamplePacket):
        """Data is stored in temp buffer, once a while the buffer is flushed to a file."""
        self._buffer += self._bytes_from_packet(packet)
        self._number_of_samples += 1
        if len(self._buffer) >= BUF_SIZE:
            self._flush_buffer()

    def finish_saving(self):
        """Close the file, return a tuple - file`s name and number of samples."""
        self._flush_buffer()
        return super().finish_saving()

    def _flush_buffer(self):
        self._write_file(self._buffer)
        self._buffer = b''

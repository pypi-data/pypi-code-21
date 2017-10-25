# -*- coding: utf-8 -*-
# Copyright (c) 2016-2018 Braintech Sp. z o.o. [Ltd.] <http://www.braintech.pl>
# All rights reserved.

"""
Module defines single :class 'DataRawWriteProxy'.

Author:
    Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
"""
import numpy

from .data_generic_write_proxy import DataGenericWriteProxy, SamplePacket
from .signal_constants import SAMPLE_NUMPY_TYPES


class DataRawWriteProxy(DataGenericWriteProxy):
    """Subclass of class 'DataGenericWriteProxy', saves raw data into file."""

    def __init__(self, p_file_path, p_append_ts=False, p_sample_type='FLOAT'):
        """Open p_file_path file for writing."""
        super().__init__(p_file_path, 'wb')
        self._append_ts = p_append_ts
        try:
            self._sample_numpy_type = SAMPLE_NUMPY_TYPES[p_sample_type]
        except KeyError:
            raise Exception('Invalid sample type to write: ' + p_sample_type)

    def data_received(self, packet: SamplePacket):
        """Write sample packet to file."""
        self._write_file(self._bytes_from_packet(packet))
        self._number_of_samples += 1

    def _bytes_from_packet(self, packet: SamplePacket):
        if self._append_ts:
            samples = numpy.hstack((packet.samples, (packet.ts - self._first_sample_timestamp)[:, numpy.newaxis]))
        else:
            if isinstance(packet, SamplePacket):
                samples = packet.samples
            else:
                samples = packet
        binary_data = samples.astype(self._sample_numpy_type, copy=False).tobytes(order='C')
        return binary_data

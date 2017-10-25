# -*- coding: utf-8 -*-
# Copyright (c) 2016-2018 Braintech Sp. z o.o. [Ltd.] <http://www.braintech.pl>
# All rights reserved.

"""
Module defines single :class: 'DataAsciiWriteProxy'.

Author:
    Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
"""
from .data_generic_write_proxy import DataGenericWriteProxy, SamplePacket


class DataAsciiWriteProxy(DataGenericWriteProxy):
    """Subclass write data in ASCII format to file."""

    def __init__(self, p_file_path):
        """Open p_file_path file for writing."""
        super().__init__(p_file_path, 'wt')

    def data_received(self, packet: SamplePacket):
        """
        Method gets and saves next sample of signal.

        :param packet: 'SamplePacket'
        """
        self._write_file(str(packet.samples.tolist()) + '\n')
        self._number_of_samples += 1

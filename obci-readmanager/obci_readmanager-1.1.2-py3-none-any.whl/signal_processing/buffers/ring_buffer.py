# -*- coding: utf-8 -*-
# Copyright (c) 2016-2018 Braintech Sp. z o.o. [Ltd.] <http://www.braintech.pl>
# All rights reserved.

"""Module provides single class representing buffer."""
import numpy

from . import ring_buffer_base


class RingBuffer(ring_buffer_base.RingBufferBase):
    """Subclass 'RingBufferBase' representing  buffer."""

    def _get_normal(self, start, end):
        return self.buffer[:, start:end]

    def _get_concat(self, start, end):
        return numpy.concatenate((self.buffer[:, start:],
                                  self.buffer[:, :end]),
                                 axis=1)

    def _add(self, s):
        for i in range(self.number_of_channels):
            self.buffer[i, self.index] = s[i]

    def _init_buffer(self):
        self.buffer = numpy.zeros((self.number_of_channels,
                                   self.size), dtype='float')

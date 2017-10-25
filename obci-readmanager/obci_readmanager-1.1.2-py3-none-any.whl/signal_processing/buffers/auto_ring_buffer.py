# -*- coding: utf-8 -*-
# Copyright (c) 2016-2018 Braintech Sp. z o.o. [Ltd.] <http://www.braintech.pl>
# All rights reserved.

"""Module provides single class representing sample packet buffer."""

from . import ring_buffer as rbn


class AutoRingBuffer(object):
    """Class representing sample packet buffer. When full calls ret_func."""

    def __init__(self, from_sample, samples_count, every, num_of_channels, ret_func, copy_on_ret):
        """
        When full, calls ret_func(d), where d is numpy array with <samples_count>samples from <num_of_channels>channels.

        Skips samples before next ret_func call.

        :param from_sample: size of the buffer
        :param samples_count: number of samples to return
        :param every: interval (number of samples to skip) before next return
        :param num_of_channels: number of channels in the returned signal
        :param ret_func: function to call when return. Takes returned samples.
        :param copy_on_ret: if true make deep copy of the buffer while processing
        """
        assert (samples_count > 0)
        assert (from_sample > 0)
        assert (every > 0)
        assert (num_of_channels > 0)

        self.every = every
        self.ret_func = ret_func

        self.whole_buf_len = from_sample
        self.ret_buf_len = samples_count

        self.count = 0
        self.is_full = False

        self.buffer = rbn.RingBuffer(from_sample,
                                     num_of_channels,
                                     copy_on_ret)

    def clear(self):
        """Clear buffer."""
        self.count = 0
        self.is_full = False
        self.buffer.clear()

    def handle_sample_packet(self, sample_packet):
        """
        Handler supports packets in a manner consistent with AutoBlinkBuffer.

        :param sample_packet: signal as SamplePackage class
        :return: None
        """
        for idx in range(len(sample_packet.ts)):
            self._handle_sample(sample_packet.samples[idx])

    def _handle_sample(self, s):
        self.buffer.add(s)
        self.count += 1
        if not self.is_full:
            if self.count == self.whole_buf_len:
                self.is_full = True
                self.count %= self.every
                if self.count == 0:
                    self.count = self.every

        if self.is_full and self.count == self.every:
            d = self.buffer.get(0, self.ret_buf_len)
            self.ret_func(d)
            self.count = 0

# -*- coding: utf-8 -*-
# Copyright (c) 2016-2018 Braintech Sp. z o.o. [Ltd.] <http://www.braintech.pl>
# All rights reserved.

"""Module provides classes representing single blink and blink buffers."""
import collections
import numpy

from . import ring_buffer as rbn

Sample = numpy.zeros


class Blink:
    """:class:'Blink' initializes packet of a blink."""

    def __init__(self, timestamp, index):
        """Initialize packet of a blink."""
        self.timestamp = timestamp
        self.index = index


class BlinkEntry(object):
    """Class representing single blink."""

    def __init__(self, blink: Blink, blink_count: int, blink_pos: int) -> None:
        """
        Blink variable as a representation of the stimulus.

        :param blink: variable Blink (object with one field named timestamp)
        :param blink_count: index of the stimulus
        :param blink_pos: position of the stimulus in relation to the indexes of the samples in the buffer.
        """
        self.blink = blink
        self.count = blink_count
        self.position = blink_pos


class AutoBlinkBuffer(object):
    """
    Class representing buffer which returns predefined epochs of signal around some blink event.

    Ex. to use in event related potential paradigms.
    """

    def __init__(self, from_blink, samples_count, num_of_channels, sampling, ret_func, copy_on_ret):
        """
        After occurrence of the blink and getting a sufficient number of samples calls ret_func(blink, d).

        Blink is a Blink variable and d is a corresponding numpy array with
        <samples_count> samples from <num_of_channels> channels.

        :param from_blink: blink from which start collecting samples
        :param samples_count: number of samples to return
        :param num_of_channels: number of channels to return
        :param sampling: sampling frequency
        :param ret_func: function to call when return. Takes returned samples.
        :param copy_on_ret: if true make deep copy of the buffer while processing
        """
        assert (samples_count > 0)
        assert (num_of_channels > 0)

        self.ret_func = ret_func
        self.ret_buf_len = samples_count  # 1024
        self.blink_from = from_blink  # 128
        self.sampling = sampling  # float(1024)
        self.curr_blink = None
        self.curr_blink_ts = None
        self.count = 0
        self.blinks_count = 0
        self.is_full = False
        self.whole_buf_len = (self.ret_buf_len + abs(self.blink_from)) * 2

        self.buffer = rbn.RingBuffer(self.whole_buf_len, num_of_channels,
                                     copy_on_ret)

        self.times = rbn.RingBuffer(self.whole_buf_len,
                                    1, copy_on_ret)
        self.times_sample = Sample(1)
        self.blinks = collections.deque()

    def clear(self):
        """Clear buffer."""
        self.count = 0
        self.is_full = False
        self.buffer.clear()
        self.times.clear()
        self._clear_blinks()

    def _clear_blinks(self):
        self.blinks_count = 0
        self.blinks.clear()

    def handle_blink(self, blink: Blink) -> None:
        """
        Method which assigns index and position to the Blink and queues this Blink.

        :param blink: Blink (object with one field named timestamp)
        :return:
        """
        if not self.is_full:
            print("AutoBlinkBuffer - Got blink before buffer is full. Ignore!")
            return
        blink_ts = blink.timestamp + (self.blink_from / self.sampling)
        blink_pos = self._get_times_index(blink.timestamp)
        if blink_pos < 0:
            return
        elif blink_pos >= self.whole_buf_len:
            # nie ma jeszcze nawet pierwszej probki
            blink_count = self.ret_buf_len + int(
                self.sampling * (blink_ts - self._get_times_last()))
            blink_pos = self.whole_buf_len - self.ret_buf_len
        else:
            # gdzies w srodku
            blink_count = self.ret_buf_len - (self.whole_buf_len - blink_pos)
            if blink_count < 0:
                blink_count = 0
            blink_pos -= blink_count

        if not len(self.blinks) == 0:
            blink_count -= self.blinks_count  # last.count #get_last_blink()

        b = BlinkEntry(blink, blink_count, blink_pos)
        self.blinks.append(b)
        self.blinks_count += blink_count
        # [10, 15, 18, 22]

    def handle_sample_packet(self, sample_packet):
        """
        Method handles signal sample packets in a manner consistent with AutoBlinkBuffer.

        :param sample_packet: signal as a SamplePacket class.
        :return: None
        """
        for idx in range(len(sample_packet.ts)):
            self._handle_sample(sample_packet.samples[idx], sample_packet.ts[idx])

    def _handle_sample(self, s, t):
        self.buffer.add(s)
        self.times_sample[0] = t
        self.times.add(self.times_sample)
        self.count += 1

        if not self.is_full:
            self.is_full = (self.count == self.whole_buf_len)
        else:
            if not len(self.blinks) == 0:
                curr = self.blinks[0]
                curr.count -= 1
                self.blinks_count -= 1
                if curr.count <= 0:
                    curr = self.blinks.popleft()
                    d = self.buffer.get(curr.position, self.ret_buf_len)
                    self.ret_func(curr.blink, d)

    def _get_times_index(self, value):
        if self.is_full:
            last = self.whole_buf_len
        else:
            last = self.count
        vect = self.times.get(0, last)[0]
        ret = -1
        for i, v in enumerate(vect):
            if value < v:
                return ret
            ret = i
        return self.whole_buf_len

    def _get_times_last(self):
        if self.is_full:
            last = self.whole_buf_len
        else:
            last = self.count
        return self.times.get(0, last)[0][last - 1]

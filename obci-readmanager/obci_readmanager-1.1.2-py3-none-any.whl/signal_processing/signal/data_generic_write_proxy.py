# -*- coding: utf-8 -*-
# Copyright (c) 2016-2018 Braintech Sp. z o.o. [Ltd.] <http://www.braintech.pl>
# All rights reserved.

"""
Module providing :class 'DataGenericWriteProxy' representing data file.

Author:
    Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
"""
import abc
import numpy

from . import signal_logging as logger

LOGGER = logger.get_logger('data_generic_write_proxy', 'info')


class SamplePacket:
    """A packet of samples."""

    def __init__(self, samples: numpy.ndarray, ts: numpy.ndarray):
        """
        Initialize packet of samples.

        :param samples: numpy 2D array of size (sample_count, channel_count)
        :param ts: numpy 1D array of size sample_count
        """
        if len(samples.shape) != 2 or len(ts.shape) != 1 or samples.shape[0] != ts.shape[0]:
            raise Exception("invalid data dimensions: samples~{} ts~{}".format(samples.shape, ts.shape))
        self._samples = samples
        self._ts = ts

    @property
    def samples(self):
        """Return samples."""
        return self._samples

    @property
    def ts(self):
        """Return timestamps."""
        return self._ts

    @property
    def sample_count(self):
        """Return sample count."""
        return self._samples.shape[0]

    @property
    def channel_count(self):
        """Return channel count."""
        return self._samples.shape[1]

    def __eq__(self, other):
        """Equality operator."""
        if (self.samples == other.samples).all() and (self.ts == other.ts).all():
            return True
        else:
            return False


class DataGenericWriteProxy(metaclass=abc.ABCMeta):
    """
    A class representing data file.

    It should be an abstraction for saving raw data into a file.
    Decision whether save signal to one or few separate files should be made here
    and should be transparent regarding below interface - the interface should remain untouched.

    Public interface:

    * finish_saving() - closes data file and return its path,
    * data_received(sample_packet) - gets and saves next sample of signal
    """

    def __init__(self, file_path, file_mode):
        """Open p_file_path file for writing."""
        self._number_of_samples = 0
        self._file_path = file_path
        self._first_sample_timestamp = 0

        try:
            self._file = open(file_path, file_mode)
        except IOError:
            LOGGER.error("Error! Can`t create a file!!!. path: {}".format(self._file_path))
            raise

    @abc.abstractmethod
    def data_received(self, packet: SamplePacket):
        """Should be implemented in subclass."""
        pass

    def set_first_sample_timestamp(self, timestamp):
        """Set first sample timestamp."""
        self._first_sample_timestamp = timestamp

    def finish_saving(self):
        """Close the file, return a tuple - file`s name and number of samples."""
        self._file.flush()
        self._file.close()
        return self._file_path, self._number_of_samples

    def _write_file(self, data):
        try:
            self._file.write(data)
        except ValueError:
            LOGGER.error("Warning! Trying to write data to closed data file!")
            return

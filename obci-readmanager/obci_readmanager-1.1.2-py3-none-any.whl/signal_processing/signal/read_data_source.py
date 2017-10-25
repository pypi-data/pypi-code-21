# -*- coding: utf-8 -*-
# Copyright (c) 2016-2018 Braintech Sp. z o.o. [Ltd.] <http://www.braintech.pl>
# All rights reserved.

"""
This module provides classes for managing data source.

Author:
     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
"""
import copy
from typing import Optional, Union

import numpy

from . import data_read_proxy
from . import signal_exceptions
from . import signal_logging as logger

LOGGER = logger.get_logger('data_source', 'info')


class DataSource:
    """Base DataSource class."""

    def get_samples(self, p_from: Optional[int] = None, p_len: Optional[int] = None):
        """Method must be implemented in subclass."""
        LOGGER.error("The method must be subclassed")

    def iter_samples(self):
        """Method must be implemented in subclass."""
        LOGGER.error("The method must be subclassed")

    def __deepcopy(self, memo):
        return MemoryDataSource(copy.deepcopy(self.get_samples()))


class MemoryDataSource(DataSource):
    """Subclass of class 'DataSource', stores data in memory in 'dict' structure."""

    def __init__(self, p_data=None, p_copy=True, p_sample_source='FLOAT'):
        """
        Initialize p_data. If :param p_data is None, data is an empty array.

        :param p_data: vector of data
        :param p_copy: 'bool', if True copy p_data to data
        :param p_sample_source: 'str', type of data
        """
        super().__init__()
        self._data = None
        if p_data is not None:
            self.set_samples(p_data, p_copy)

    def set_samples(self, p_data, p_copy=True):
        """Set data samples."""
        if p_copy:
            self._data = numpy.array(p_data)
        else:
            self._data = p_data

    def set_sample(self, p_sample_index, p_sample):
        """
        Set sample.

        Throws:
        - IndexError if p_sample_index is out of range
        - ValueError if len(p_sample) does not fit number_of_channels
        """
        self._data[:, p_sample_index] = p_sample

    def get_samples(self, p_from: Optional[int] = None, p_len: Optional[int] = None):
        """Method always success. If p_from or p_len is somehow out of range return an empty array of samples."""
        if p_from is None:
            return self._data
        else:
            ret = self._data[:, p_from:(p_from + p_len)]
            if ret.shape[1] != p_len:
                raise signal_exceptions.NoNextValue()
            else:
                return ret

    def iter_samples(self):
        """Return every sample in data vector."""
        for i in range(len(self._data[0])):
            yield self._data[:, i]


class FileDataSource(DataSource):
    """Subclass of class 'DataSource', gets data from memory or from given file."""

    def __init__(self, p_file: Union[str, data_read_proxy.DataReadProxy], p_num_of_channels, p_sample_type="FLOAT"):
        """
        Initialize data_proxy.

        :param p_file: 'str', name of file containing data samples
        :param p_num_of_channels: number of channels
        :param p_sample_type: type of data's samples
        """
        super().__init__()
        self._num_of_channels = p_num_of_channels
        self._mem_source = None
        if isinstance(p_file, str):
            self._data_proxy = data_read_proxy.DataReadProxy(p_file, sample_type=p_sample_type)
        else:
            self._data_proxy = p_file

    def get_samples(self, p_from: Optional[int] = None, p_len: Optional[int] = None) -> numpy.ndarray:
        """
        If we have data in memory: get samples.

        Else if p_from is None (no data in-memory):
            * whole data set is requested load data from file and get_samples(), next cache data;
            * a piece of data is requested get samples from get_next_values().

        :param p_from: 'str', name of file containing data samples
        :param p_len: length of data
        :return: data: numpy.ndarray
        """
        if self._mem_source:
            # we have data in-memory
            return self._mem_source.get_samples(p_from, p_len)
        elif p_from is None:
            # we don't have data in-memory
            # and whole data set is requested
            # so let`s use the occasion and cache data
            LOGGER.info("All data set requested for the first time. Start reading all data from the file...")
            vals = self._data_proxy.get_all_values(self._num_of_channels)
            self._mem_source = MemoryDataSource(vals, False)
            return self._mem_source.get_samples()

        else:
            # we don't have data in-memory
            # only a piece of data is requested
            self._data_proxy.goto_value(p_from * self._num_of_channels)
            d = self._data_proxy.get_next_values(self._num_of_channels * p_len)
            return numpy.reshape(d, (self._num_of_channels, -1), 'f')

    def set_samples(self, samples, copy):
        """
        If copy is True: copy :param samples to MemoryDataSource if memory source exist.

        Else set samples as memory source.
        """
        if self._mem_source is None:
            self._mem_source = MemoryDataSource(samples, copy)
        else:
            self._mem_source.set_samples(samples, copy)

    def iter_samples(self):
        """Generator, iterates sample by sample.."""
        if self._mem_source:
            for samp in self._mem_source.iter_samples():
                yield samp
        else:
            self._data_proxy.finish_reading()
            self._data_proxy.start_reading()
            while True:
                try:
                    samp = numpy.zeros(self._num_of_channels)
                    samp[:] = self._data_proxy.get_next_values(self._num_of_channels)
                    yield samp
                except signal_exceptions.NoNextValue:
                    self._data_proxy.finish_reading()
                    break

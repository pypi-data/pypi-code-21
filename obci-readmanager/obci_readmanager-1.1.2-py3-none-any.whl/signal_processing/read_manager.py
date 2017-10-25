# -*- coding: utf-8 -*-
# Copyright (c) 2016-2018 Braintech Sp. z o.o. [Ltd.] <http://www.braintech.pl>
# All rights reserved.

"""
Module provides single :class 'ReadManager' responsible for reading OpenBCI file format.

Author:
    Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
"""

import copy
import os.path
from typing import Union

import numpy

from .mne_utils.read_manager_mne_mixin import ReadManagerMNEMixin
from . import logging as logger
from .signal import data_raw_write_proxy
from .signal import info_file_proxy
from .signal import read_data_source
from .signal import read_info_source
from .tags import read_tags_source
from .tags import tags_file_writer

LOGGER = logger.get_logger('read_manager', 'info')


class ReadManager(ReadManagerMNEMixin):
    """
    A class responsible for reading OpenBCI file format.

    Public interface:

    * start_reading() - open info and data file,
    * get_next_value() - get next value from data file,
    * get_param(param_name) - get param_name parameter from info file.

    Wanna be able to read a new parameter 'new_param'?

    #. Register reading function in self._create_info_tags_control() under 'new_param' key.
    #. Implement the function (it should be considered as class private function, not callable from outside;
       the function should return a value for 'new_param' request).
    #. Call ``get_param('new_param')`` every time you want to get the param.
    """

    def __init__(self,
                 p_info_source: Union[str, read_info_source.FileInfoSource],
                 p_data_source: Union[str, read_data_source.FileDataSource],
                 p_tags_source: Union[str, read_tags_source.FileTagsSource]):
        """Initialize FileInfoSource, FileDataSource and FileTagsSource."""
        super().__init__()

        if isinstance(p_info_source, str):
            self.info_source = read_info_source.FileInfoSource(p_info_source)
        else:
            self.info_source = p_info_source

        if isinstance(p_data_source, str):
            self.data_source = read_data_source.FileDataSource(
                p_data_source,
                int(self.info_source.get_param('number_of_channels')),
                self.info_source.get_param('sample_type')
            )
        else:
            self.data_source = p_data_source

        if isinstance(p_tags_source, str):
            self.tags_source = read_tags_source.FileTagsSource(p_tags_source)
        else:
            self.tags_source = p_tags_source

    def __deepcopy__(self, memo):
        """Construct a new object, next recursively, inserts copies into it."""
        info_source = copy.deepcopy(self.info_source)
        tags_source = copy.deepcopy(self.tags_source)
        samples_source = copy.deepcopy(self.data_source)
        return ReadManager(info_source, samples_source, tags_source)

    def save_to_file(self, p_dir: str, p_name: str):
        """Save to file (tags, info, data)."""
        path = os.path.join(p_dir, p_name)

        tags = self.get_tags()
        params = self.get_params()

        # store tags
        tags_writer = tags_file_writer.TagsFileWriter(path + '.obci.tag')
        for tag in tags:
            tags_writer.tag_received(tag)

        # store info
        info_writer = info_file_proxy.InfoFileWriteProxy(path + '.obci.xml')
        info_writer.set_attributes(params)

        # store data
        p_sample_type = self.get_param('sample_type')
        data_writer = data_raw_write_proxy.DataRawWriteProxy(path + '.obci.raw', p_sample_type=p_sample_type)
        for sample in self.iter_samples():
            data_writer.data_received(sample)

        tags_writer.finish_saving(0)
        info_writer.finish_saving()
        data_writer.finish_saving()

    def get_samples(self, p_from=None, p_len=None, p_unit='sample') -> numpy.ndarray:
        """
        Return a two dimensional array of signal values.

        :param p_from:
        :param p_len:
        :param p_unit: can be 'sample' or 'second' and makes sense only if p_from and p_len is not ``None``.
        :return: numpy array
        """
        if p_unit == 'sample':
            return self.data_source.get_samples(p_from, p_len)
        elif p_unit == 'second':
            sampling = int(float(self.get_param('sampling_frequency')))
            return self.data_source.get_samples(int(p_from * sampling), int(p_len * sampling))
        else:
            raise Exception('Unrecognised unit type. Should be sample or second!. Abort!')

    def get_microvolt_samples(self, *args, **kwargs):
        """
        Return a two dimensional array of signal values - adjusted to microvolts.

        :param p_from:
        :param p_len:
        :param p_unit: can be 'sample' or 'second' and makes sense only if p_from and p_len is not ``None``.
        :return: numpy array
        """
        gains = numpy.array([float(i) for i in self.get_param('channels_gains')])[:, numpy.newaxis]

        offsets = numpy.array([float(i) for i in self.get_param('channels_offsets')])[:, numpy.newaxis]

        return self.get_samples(*args, **kwargs) * gains + offsets

    def get_all_samples(self):
        """Return an array of all samples."""
        return self.get_samples(p_from=None, p_len=None, p_unit='sample')

    def get_channel_samples(self, p_ch_name, p_from=None, p_len=None, p_unit='sample'):
        """
        Return an array of values for channel p_ch_name.

        Raise ValueError exception if there is no channel with that name.

        p_unit can be 'sample' or 'second' and makes sense only if p_from and p_len is not none.
        """
        ch_ind = self.get_param('channels_names').index(p_ch_name)  # TODO error
        return self.get_samples(p_from, p_len, p_unit)[ch_ind]

    def get_channels_samples(self, p_ch_names, p_from=None, p_len=None, p_unit='sample'):
        """Return an array of values for channel p_ch_names."""
        assert (len(p_ch_names) > 0)
        s = self.get_channel_samples(p_ch_names[0], p_from, p_len, p_unit)
        for ch in p_ch_names[1:]:
            s = numpy.vstack((s, self.get_channel_samples(ch, p_from, p_len, p_unit)))
        return s

    def set_samples(self, p_samples, p_channel_names, p_copy=False):
        """
        Set new samples and channel names.

        :param p_samples: 2 dimensional numpy array (n_channels x n_samples)
        :param p_channel_names:  list of strings, names of the channels. Should be the same length as p_samples.shape[0]
        :param p_copy: True if you want to make a copy of the p_samples array
        """
        try:
            dim = p_samples.ndim
        except AttributeError:
            raise Exception("Samples not a numpy array!")
        if dim != 2:
            raise Exception("Samples must be a 2-dim numpy array!")
        num_of_channels = p_samples.shape[0]
        num_of_samples = p_samples.shape[1]

        if len(p_channel_names) != num_of_channels:
            raise Exception("Number of channels names is different from number of channels in samples!")

        self.set_param('channels_names', p_channel_names)
        self.set_param('number_of_channels', num_of_channels)
        self.set_param('number_of_samples', num_of_samples)
        self.data_source.set_samples(p_samples, p_copy)

    def get_tags(self, p_tag_type=None, p_from=None, p_len=None, p_func=None):
        """Return all tags of type tag_type, or all types if tag_type is None."""
        if self.tags_source is None:
            return []
        else:
            return self.tags_source.get_tags(p_tag_type, p_from, p_len, p_func)

    def set_tags(self, p_tags):
        """Set tags for :given type of tags."""
        if self.tags_source is not None:
            self.tags_source.set_tags(p_tags)
        else:
            self.tags_source = read_tags_source.MemoryTagsSource(p_tags)

    def get_param(self, p_param_name):
        """
        Return parameter value for p_param_name:str.

        Raise NoParameter exception if p_param_name parameters was not found.
        """
        return self.info_source.get_param(p_param_name)

    def get_params(self):
        """Get params from info_source."""
        return self.info_source.get_params()

    def set_param(self, p_key, p_value):
        """Set param (p_key, p_value) in info_source."""
        self.info_source.set_param(p_key, p_value)

    def set_params(self, p_params):
        """Set params in info_source."""
        self.info_source.update_params(p_params)

    def reset_params(self):
        """Reset params in info source."""
        self.info_source.reset_params()

    def iter_tags(self, p_tag_type=None, p_from=None, p_len=None, p_func=None):
        """
        Generator, iterates tag by tag (of given type).

        :param p_tag_type: type of tag
        :param p_from: start timestamp
        :param p_len: number of tag
        :param p_func: logic  who to choose tag eg. tag['desc'][u'index'] == tag['desc'][u'target']
        :return: tag or None
        """
        if self.tags_source is None:
            return
        for tag in self.tags_source.get_tags(p_tag_type, p_from, p_len, p_func):
            yield tag

    def iter_samples(self):
        """Generator, iterates sample by sample."""
        for s in self.data_source.iter_samples():
            yield s

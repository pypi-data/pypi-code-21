# -*- coding: utf-8 -*-
# Copyright (c) 2016-2018 Braintech Sp. z o.o. [Ltd.] <http://www.braintech.pl>
# All rights reserved.

"""Wii preprocessing."""
from __future__ import print_function, division
from ..signal import read_data_source
from ..tags import smart_tag_definition
from .. import smart_tags_manager
import copy
from .raw_preprocessing import raw_downsample_signal, raw_filter_signal
from .wii_read_manager import WBBReadManager


def wii_downsample_signal(wbb_mgr, factor=2, pre_filter=False, use_filtfilt=False):
    """Return WBBReadManager object with downsampled signal values.

    Input:
    wbb_mgr 			-- WBBReadManager object
    factor 				-- int 	-- downsample signal to sampling rate original_sampling_frequency / factor
    pre_filter 			-- bool -- use lowpass filter with cutoff frequency sampling_frequency / 2
    use_filtfilt 		-- bool -- use filtfilt in filtering procedure (default lfilter)
    """
    if pre_filter:
        fs = float(wbb_mgr.get_param('sampling_frequency'))
        wbb_mgr = wii_filter_signal(wbb_mgr, fs / 2, 4, use_filtfilt)
        samples = wbb_mgr.get_all_samples()
    else:
        samples = wbb_mgr.get_all_samples()

    new_samples = raw_downsample_signal(samples, factor)

    info_source = copy.deepcopy(wbb_mgr.info_source)
    info_source.get_params()['number_of_samples'] = str(len(new_samples[0]))
    info_source.get_params()['sampling_frequency'] = str(float(wbb_mgr.get_param('sampling_frequency')) / factor)
    tags_source = copy.deepcopy(wbb_mgr.tags_source)
    samples_source = read_data_source.MemoryDataSource(new_samples)
    return WBBReadManager(info_source, samples_source, tags_source)


def wii_filter_signal(wbb_mgr, cutoff_upper, order, use_filtfilt=False):
    """Return WBBReadManager object with filtered signal values.

    Input:
    wbb_mgr 			-- WBBReadManager object
    cutoff_upper 		-- float -- cutoff frequency
    order 				-- int   -- order of filter
    use_filtfilt 		-- bool -- use filtfilt in filtering procedure (default lfilter)
    """
    fs = float(wbb_mgr.get_param('sampling_frequency'))
    samples = wbb_mgr.get_all_samples()
    new_samples = raw_filter_signal(samples, fs, cutoff_upper, order, use_filtfilt)

    info_source = copy.deepcopy(wbb_mgr.info_source)
    tags_source = copy.deepcopy(wbb_mgr.tags_source)
    samples_source = read_data_source.MemoryDataSource(new_samples)
    return WBBReadManager(info_source, samples_source, tags_source)


def wii_fix_sampling(wbb_mgr):
    """Wii fix samling (not)."""
    return


def wii_cut_fragments(wbb_mgr, start_tag_name='start', end_tags_names=['stop']):
    """Return SmartTags object with cut signal fragments according to 'start' - 'stop' tags."""
    x = smart_tag_definition.SmartTagEndTagDefinition(start_tag_name=start_tag_name,
                                                      end_tags_names=end_tags_names)
    smart_mgr = smart_tags_manager.SmartTagsManager(x, None, None, None, wbb_mgr)
    return smart_mgr.get_smart_tags()

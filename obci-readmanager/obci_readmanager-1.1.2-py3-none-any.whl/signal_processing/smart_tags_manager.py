# -*- coding: utf-8 -*-
# Copyright (c) 2016-2018 Braintech Sp. z o.o. [Ltd.] <http://www.braintech.pl>
# All rights reserved.

"""
Module defines single :class 'SmartTagsManager'.

Author:
    Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
"""
import queue
from typing import Optional
from functools import cmp_to_key

from .mne_utils.smart_tags_mne_mixin import SmartTagManagerMNEMixin
from . import logging as logger
from . import read_manager
from .signal import signal_exceptions
from .tags import smart_tag

LOGGER = logger.get_logger('smart_tags_manager', 'info')


class SmartTagsManager(SmartTagManagerMNEMixin):
    """
    By now manager gets in init tag definition object and dictionary of files paths.

    Regarding tag definition it iterates smart tags from file in iter_smart_tags().

    Public interface:

    * __init__()
    * iter_smart_tags()
    """

    def __init__(self,
                 p_tag_def,
                 p_info_file,
                 p_data_file,
                 p_tags_file,
                 p_read_manager: Optional[read_manager.ReadManager] = None):
        """
        Init all needed slots, read tags file, init smart tags.

        Parameters:
        - p_tag_def - an instance of tag definition object
        (see smart_tag_definition.py)
        - p_files - a dictionary with files paths:
        'info' - info file
        'data' - data file
        'tags' - tags file
        """
        super().__init__()

        if p_read_manager is None:
            self._read_manager = read_manager.ReadManager(
                p_info_file,
                p_data_file,
                p_tags_file
            )
        else:
            self._read_manager = p_read_manager

        # Init smart tags, here just create smart tags objects without
        # data slot set.

        # PUBLIC SLOTS
        self.num_of_channels = int(self._read_manager.get_param(
            'number_of_channels'))
        l_freq_str = self._read_manager.get_param('sampling_frequency')
        self.sampling_freq = float(l_freq_str)
        # PUBLIC SLOTS
        self._sample_duration = 1 / float(self.sampling_freq)

        self._first_sample_ts = 0.0
        try:
            self._first_sample_ts = self._read_manager.get_start_timestamp()
        except AttributeError:
            pass

        self._smart_tags = []
        self._init_smart_tags(p_tag_def)

    def __str__(self):
        """Return string representation of: tags_num, num_of_channels, sampling_freq."""
        return str({'tags_num': len(self._smart_tags),
                    'num_of_channels': self.num_of_channels,
                    'sampling_freq': self.sampling_freq})

    def get_read_manager(self):
        """"Init smart tags."""
        return self._read_manager

    def _init_smart_tags(self, p_tag_def):
        """Init smart tags depending on given smart tag definition."""
        LOGGER.info("Start initialising smart tags.")

        try:
            l_defs = list(p_tag_def)
        except TypeError:
            l_defs = [p_tag_def]

        for i_def in l_defs:
            if i_def.is_type("duration"):
                self._init_duration_smart_tags(i_def)
                LOGGER.info("Finished initialising smart tags.")
            elif i_def.is_type("end_tag"):
                self._init_end_tag_smart_tags(i_def)
                LOGGER.info("Finished initialising smart tags.")
            else:
                LOGGER.error("Unrecognised tag definition type.")
                raise Exception("Unrecognised tag definition type.")

        def cmp_tags(t1, t2):
            ts1 = t1['start_timestamp']
            ts2 = t2['start_timestamp']
            if ts1 == ts2:
                return 0
            elif ts1 > ts2:
                return 1
            else:
                return -1

        self._smart_tags.sort(key=cmp_to_key(cmp_tags))

    def _init_end_tag_smart_tags(self, p_tag_def):
        """
        Read all tags from file - create smart tags objects while doing it.

        End-tag-smart-tag is tag that begins and end with some particular tag.
        """
        l_st_queue = queue.Queue()  # Tags waiting for end tag
        for i_tag in self._read_manager.iter_tags():
            if i_tag['name'] in p_tag_def.end_tags_names:
                # Ending tag is met - set this tag to all smart tags waiting
                # in the queue
                while True:
                    try:
                        i_st = l_st_queue.get_nowait()
                    except:
                        break
                    i_st.set_end_tag(i_tag)
                    self._smart_tags.append(i_st)
            if i_tag['name'] == p_tag_def.start_tag_name:
                # Create new smart tag, append it to queue
                st = smart_tag.SmartTagEndTag(p_tag_def, i_tag)
                if 'self' in p_tag_def.end_tags_names:
                    # end_tags_names contains 'self' literal which means
                    # that st`s end tag is its start tag
                    st.set_end_tag(i_tag)
                    self._smart_tags.append(st)
                else:
                    l_st_queue.put(st)

    def _init_duration_smart_tags(self, p_tag_def):
        """
        Read all tags from file - create smart tags objects while doing it.

        Duration-smart-tag is tag that begins with some particular tag.
        """
        for i_tag in self._read_manager.iter_tags(p_tag_def.start_tag_name):
            LOGGER.debug("Got tag in _init_duration_smart_tags: " + str(i_tag))
            LOGGER.debug("Want tag: " + str(p_tag_def.start_tag_name) + ". Got tag: " + str(i_tag['name']))
            st = smart_tag.SmartTagDuration(p_tag_def, i_tag)
            self._smart_tags.append(st)

    def get_smart_tags(self, p_tag_type=None, p_from=None, p_len=None, p_func=None):
        """Get smart_stag of given tag type."""
        sts = [t for t in self.iter_smart_tags()]
        return self.get_read_manager().tags_source._filter_tags(
            sts, p_tag_type, p_from, p_len, p_func)

    def iter_smart_tags(self):
        """
        It iterates SmartTag objects.

        You can call get_data() on smart tag, and you will get samples for all channels for that smart tag in format:
        [[list of all samples from ch 0], [list of all samples from ch 1] ...]

        This is an iterator, so use it like::

            for i in mgr.iter_smart_tags():
                pass
        """
        LOGGER.debug("FIRST SAMPLE TIMESTMP: " + str(self._first_sample_ts))

        last_duration_ts = -1
        last_duration_id = -1

        for i, i_st in enumerate(self._smart_tags):
            try:
                if i_st.is_initialised():
                    yield i_st
                    continue

                # First needed sample timestamp
                l_start_ts = i_st.get_start_timestamp()
                # Last needed sample timestamp
                l_end_ts = i_st.get_end_timestamp()
                # duration
                duration_ts = l_end_ts - l_start_ts

                # same in samples
                l_samples_to_start = int((l_start_ts - self._first_sample_ts) * self.sampling_freq)
                l_duration_temp = int(l_end_ts * self.sampling_freq) - int(l_start_ts * self.sampling_freq)

                # code is written in such way, that guarantees that signal taken from tag to tag for all tags
                # is sequential, without gaps and without overlaps
                # but that doesnt guarantee that tags with same duration will generate signal with same
                # sample length. Here we fix this:

                # if durations of this tag and last one should be the same sample-wise:
                if abs(last_duration_ts - duration_ts) < 1 / self.sampling_freq:
                    l_duration = last_duration_id
                else:
                    l_duration = l_duration_temp
                last_duration_id = l_duration
                last_duration_ts = duration_ts

                l_samples_to_end = l_samples_to_start + l_duration

                LOGGER.debug("Tag start timestamp: " + str(l_start_ts))
                LOGGER.debug("To start tag samples:: " + str(l_samples_to_start))
                LOGGER.debug("Tag end timestamp: " + str(l_end_ts))
                LOGGER.debug("Tag end tag samples: " + str(l_samples_to_end))

                LOGGER.debug("SAMPLES NO START: " + str(l_samples_to_start))
                l_data = self._read_manager.get_samples(l_samples_to_start, l_duration)
                l_tags = self._read_manager.get_tags(None, l_start_ts, (l_end_ts - l_start_ts))
                l_info = self._read_manager.get_params()
                l_info['number_of_samples'] = l_duration * l_info['number_of_channels']
                # TODO set some l_info parameters
                LOGGER.debug("SAMPLES NO END: " + str(l_samples_to_end))

                # Now l_data contains samples from all channels between
                # l_start and l_end timestamp
                i_st.data_source.set_samples(l_data)
                i_st.info_source.set_params(l_info)
                i_st.tags_source.set_tags(l_tags)
                i_st.set_initialised()
                yield i_st  # Return smart tag filled with data
            except signal_exceptions.NoNextValue:
                LOGGER.info("No samples left. Some smart tags could have been ignored, probably " + str(
                    len(self._smart_tags) - i) + " of " + str(len(self._smart_tags)) + " tags.")
                break  # Exit the loop, end iterator
        LOGGER.debug("Finished smart tags iteration")
        # Reset samples count so that next
        # iter_smart_tags call will work

    def __iter__(self):
        """Provide integration over smart_tags."""
        return self.iter_smart_tags()

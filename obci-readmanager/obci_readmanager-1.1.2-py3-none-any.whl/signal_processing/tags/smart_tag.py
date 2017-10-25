# -*- coding: utf-8 -*-
# Copyright (c) 2016-2018 Braintech Sp. z o.o. [Ltd.] <http://www.braintech.pl>
# All rights reserved.

"""Implement Smart tags classes: SmartTagEndTag, SmartTagDuration."""
from . import read_tags_source
from .. import read_manager
from ..signal import read_data_source
from ..signal import read_info_source


class SmartTag(read_manager.ReadManager):
    """Subclass of :class 'ReadManager' provides all info from MemoryInfo- MemoryData-, and MemoryTagsSource."""

    def __init__(self, p_tag_def, p_start_tag):
        """Initialise: MemoryInfo- MemoryData-, and MemoryTagsSource."""
        super().__init__(read_info_source.MemoryInfoSource(),
                         read_data_source.MemoryDataSource(),
                         read_tags_source.MemoryTagsSource())
        self._start_tag = p_start_tag
        self._tag_def = p_tag_def
        self._is_initialised = False

    def get_start_timestamp(self):
        """Get value of first timestamp."""
        return self._tag_def.start_param_func(self._start_tag) + self._tag_def.start_offset

    def get_end_timestamp(self):
        """To be subclassed."""
        pass

    def get_start_tag(self):
        """Get start tag."""
        return self._start_tag

    def set_initialised(self):
        """Set value of :param _is_initialised = True."""
        self._is_initialised = True

    def is_initialised(self):
        """Check if initialised."""
        return self._is_initialised

    def __getitem__(self, p_key):
        """Get value of p_key 'start_timestamp', 'end_timestamp' or other."""
        if p_key == 'start_timestamp':
            return self.get_start_timestamp()
        elif p_key == 'end_timestamp':
            return self.get_end_timestamp()
        else:
            return self.get_start_tag()[p_key]


class SmartTagEndTag(SmartTag):
    """
    Subclass of :class 'SmartTag'.

    Public interface:

    * get_data() <- this is the only method to be really used outside
    * __init__(tag_def, start_tag)
    * get_start_timestamp()
    * get_end_timestamp()
    * get_data_for(channel)
    * get_start_tag()
    * get_end_tag()
    * set_data()
    * set_end_tag()
    """

    def __init__(self, p_tag_def, p_start_tag):
        """
        :param p_tag_def: must be an instance of SmartTagEndTagDefinition.

        :param p_start_tag: must be a dictionary representation of existing tag.
        """
        super(SmartTagEndTag, self).__init__(p_tag_def, p_start_tag)
        self._end_tag = None

    def set_end_tag(self, p_tag):
        """Method must be fired only and only once, to set smart tag`s ending tag."""
        self._end_tag = p_tag

    def get_end_timestamp(self):
        """Get value of last timestamp."""
        return self._tag_def.end_param_func(self._end_tag) + self._tag_def.end_offset

    def get_end_tag(self):
        """Get last tag."""
        return self._end_tag


class SmartTagDuration(SmartTag):
    """
    Subclass of :class 'SmartTag'.

    Public interface:

    * get_data() <- this is the only method to be really used outside
    * __init__(tag_def, start_tag)
    * get_start_timestamp()
    * get_end_timestamp()
    * get_data_for(channel)
    * get_start_tag()
    * set_data()
    * set_end_tag()
    """

    def get_end_timestamp(self):
        """Get value of end_timestamp."""
        return self._tag_def.start_param_func(self._start_tag) + self._tag_def.duration + self._tag_def.end_offset

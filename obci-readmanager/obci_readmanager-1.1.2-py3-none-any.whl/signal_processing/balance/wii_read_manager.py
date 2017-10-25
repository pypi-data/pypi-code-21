# -*- coding: utf-8 -*-
# Copyright (c) 2016-2018 Braintech Sp. z o.o. [Ltd.] <http://www.braintech.pl>
# All rights reserved.

"""Wii Read Manager."""
from __future__ import print_function, division
from .. import read_manager
import numpy as np
from . import wii_utils


class WBBReadManager(read_manager.ReadManager):
    """Wii Read Manager."""

    def __init__(self, *args, **kwargs):
        """Init WBBReadManager."""
        super().__init__(*args, **kwargs)
        self._get_x()
        self._get_y()

    def get_raw_signal(self):
        """Return raw sensor data (TopRight, TopLeft, BottomRight, BottomLeft)."""
        top_left = self.get_channel_samples('top_left')
        top_right = self.get_channel_samples('top_right')
        bottom_right = self.get_channel_samples('bottom_right')
        bottom_left = self.get_channel_samples('bottom_left')
        return top_right, top_left, bottom_right, bottom_left

    def get_x(self):
        """Return COPx computed from raw sensor data."""
        return self.get_channel_samples('x')

    def get_y(self):
        """Return COPx computed from raw sensor data."""
        return self.get_channel_samples('y')

    def _get_x(self):
        top_left, top_right, bottom_right, bottom_left = self.get_raw_signal()
        x, y = wii_utils.get_x_y(top_left, top_right, bottom_right, bottom_left)
        samples = self.get_all_samples()
        chann_names = self.get_param('channels_names')
        self.set_samples(np.vstack((samples, x)), chann_names + [u'x'])
        chann_off = self.get_param('channels_offsets')
        self.set_param('channels_offsets', chann_off + [u'0.0'])
        chann_gain = self.get_param('channels_gains')
        self.set_param('channels_gains', chann_gain + [u'1.0'])
        return x

    def _get_y(self):
        """Return COPy computed from raw sensor data and adds 'y' channel to ReadManager object."""
        top_left, top_right, bottom_right, bottom_left = self.get_raw_signal()
        x, y = wii_utils.get_x_y(top_left, top_right, bottom_right, bottom_left)
        samples = self.get_all_samples()
        chann_names = self.get_param('channels_names')
        self.set_samples(np.vstack((samples, y)), chann_names + [u'y'])
        chann_off = self.get_param('channels_offsets')
        self.set_param('channels_offsets', chann_off + [u'0.0'])
        chann_gain = self.get_param('channels_gains')
        self.set_param('channels_gains', chann_gain + [u'1.0'])
        return y

    def get_timestamps(self):
        """Return timestamps channel."""
        return self.get_channel_samples('TSS')

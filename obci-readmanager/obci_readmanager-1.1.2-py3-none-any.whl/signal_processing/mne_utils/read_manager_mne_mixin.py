# -*- coding: utf-8 -*-
# Copyright (c) 2016-2018 Braintech Sp. z o.o. [Ltd.] <http://www.braintech.pl>
# All rights reserved.

"""Mixin for readmanager to create MNE.Raw objects."""
import json
from typing import Union
from copy import copy
import numpy

from ..signal.signal_constants import sample_type_from_numpy
from ..signal.read_info_source import MemoryInfoSource
from ..signal.read_data_source import MemoryDataSource
from ..signal.signal_exceptions import NoParameter
from ..signal import read_info_source
from ..signal import read_data_source
from ..tags import read_tags_source

from ..mne_utils.utils import requires_mne, chtype_heuristic

try:
    import mne
except ImportError:
    pass


def add_stim_chnl(raw):
    """In place add stim channel to mne.Raw."""
    if 'STI' not in raw.ch_names:
        stim_data = numpy.zeros((1, len(raw.times)))
        info = mne.create_info(['OBCI_STIM'], raw.info['sfreq'], ['stim'])
        stim_raw = mne.io.RawArray(stim_data, info)
        raw.add_channels([stim_raw], force_update_info=True)


def _description_from_tag(tag):
    tag_desc = copy(tag)
    tag_desc.pop('start_timestamp')
    tag_desc.pop('end_timestamp')
    return json.dumps(tag_desc)


def tags_from_mne_annotations(ans):
    """Get tags from MNE.Annotations.

    :param ans: instance of MNE.Annotations
    Returns tags (list of dicts).
    """
    tags = []
    orig_time = ans.orig_time
    if orig_time is None:
        orig_time = 0
    for onset, duration, desc in zip(ans.onset, ans.duration, ans.description):
        # try to load annotations, as they would be exported by ReadManager
        # if there is no our annotations reformat them to tags
        try:
            tag = json.loads(desc)
            assert isinstance(tag, dict)
        except (json.decoder.JSONDecodeError, AssertionError):
            # MNE created not in OBCI
            tag = {'name': desc, 'desc': {}, 'channels': ''}
        tag['start_timestamp'] = onset - orig_time
        tag['end_timestamp'] = onset + duration - orig_time

        tags.append(tag)
    return tags


class ReadManagerMNEMixin:
    """Mixin for ReadManager containing MNE conversions."""

    @requires_mne
    def get_mne_info(self, channel_types=None):
        """
        Create mne.Info.

        :param: channel_types optional list of strings with channel types:
           ‘ecg’, ‘bio’, ‘stim’, ‘eog’, ‘misc’, ‘seeg’, ‘ecog’, ‘mag’, ‘eeg’, ‘ref_meg’, ‘grad’, ‘emg’, ‘hbr’ or ‘hbo’
           if None channels types will be selected heuristically.
        """
        chnames = self.get_param('channels_names')
        samplinf_freq = float(self.get_param('sampling_frequency'))
        if channel_types is None:
            channel_types = [chtype_heuristic(i) for i in chnames]

        try:
            info = mne.create_info(ch_names=chnames,
                                   sfreq=samplinf_freq,
                                   ch_types=channel_types,
                                   montage='standard_1005')
        except ValueError:  # no EEG channels at all
            info = mne.create_info(ch_names=chnames,
                                   sfreq=samplinf_freq,
                                   ch_types=channel_types)
        self._set_meas_date(info)
        return info

    @requires_mne
    def get_mne_raw(self, channel_types=None):
        """Return MNE.Raw uncut raw signal object.

        :param: channel_types optional list of strings with channel types:
           ‘ecg’, ‘bio’, ‘stim’, ‘eog’, ‘misc’, ‘seeg’, ‘ecog’, ‘mag’, ‘eeg’, ‘ref_meg’, ‘grad’, ‘emg’, ‘hbr’ or ‘hbo’
           if None channels types will be selected heuristically
        """
        data = self.get_microvolt_samples()
        # data is in microvolts, MNE for biosignal data requires volts
        data = data * 1e-6

        info = self.get_mne_info(channel_types)
        dataset = mne.io.RawArray(data, info)
        self._set_mne_tags(dataset)
        return dataset

    @classmethod
    @requires_mne
    def init_mne(cls,
                 p_info_source: Union[str, read_info_source.FileInfoSource],
                 p_data_source: Union[str, read_data_source.FileDataSource],
                 p_tags_source: Union[str, read_tags_source.FileTagsSource],
                 **kwargs):
        """Initialize FileInfoSource, FileDataSource and FileTagsSource.

        :param: channel_types optional list of strings with channel types:
           ‘ecg’, ‘bio’, ‘stim’, ‘eog’, ‘misc’, ‘seeg’, ‘ecog’, ‘mag’, ‘eeg’, ‘ref_meg’, ‘grad’, ‘emg’, ‘hbr’ or ‘hbo’
           if None channels types will be selected heuristically
        """
        return cls(p_info_source, p_data_source, p_tags_source).get_mne_raw(**kwargs)

    @classmethod
    @requires_mne
    def from_mne(cls, mne_raw):
        """Read Raw mne object to ReadManager."""
        assert isinstance(mne_raw, mne.io.BaseRaw)
        mne_raw.drop_channels(['OBCI_STIM'])
        data = mne_raw.get_data() * 1e6  # mne keeps signals in Volts
        return cls._rm_from_mne_data(data, mne_raw.info, mne_raw.annotations)

    @classmethod
    def _rm_from_mne_data(cls, data, info, annotations=None):
        mds = MemoryDataSource(data)

        mne_stamp_n = info['meas_date']
        mne_stamp_microseconds = str(mne_stamp_n[1]).rjust(6, '0').rstrip('0')
        if mne_stamp_microseconds == '':
            mne_stamp_microseconds = '0'
        mne_stamp_s = '{}.{}'.format(mne_stamp_n[0], mne_stamp_microseconds)

        chgains = [1.0] * info['nchan']
        choffsets = [0] * info['nchan']

        mis = MemoryInfoSource(p_params={'sampling_frequency': str(info['sfreq']),
                                         'channels_names': info['ch_names'],
                                         'number_of_channels': str(len(info['ch_names'])),
                                         'first_sample_timestamp': mne_stamp_s,
                                         'channels_gains': chgains,
                                         'channels_offsets': choffsets,
                                         'sample_type': sample_type_from_numpy(data.dtype),
                                         'number_of_samples': str(data.shape[1])
                                         })

        read_manager = cls(p_data_source=mds, p_info_source=mis, p_tags_source=None)
        if annotations:
            read_manager.set_tags(tags_from_mne_annotations(annotations))
        return read_manager

    def _set_meas_date(self, info):
        try:
            meas_date_l = (self.get_param('first_sample_timestamp')).split('.')
        except NoParameter:
            return
        try:
            meas_date_s = int(meas_date_l[0])
        except ValueError:
            meas_date_s = 0
        try:
            meas_date_us = int(meas_date_l[1].lstrip('0'))
        except ValueError:
            meas_date_us = 0

        meas_date = numpy.array([meas_date_s, meas_date_us], dtype=numpy.int32)
        info['meas_date'] = meas_date

    def mne_annotations(self):
        """"Get mne.Annotations from ReadManager tags."""
        onsets = []
        durations = []
        descriptions = []

        for tag in self.get_tags():
            start_t = tag['start_timestamp']
            end_t = tag['end_timestamp']
            duration = end_t - start_t
            onsets.append(start_t)
            durations.append(duration)

            descriptions.append(_description_from_tag(tag))
        return mne.Annotations(onsets, durations, descriptions)

    def mne_events(self):
        """Get mne events from ReadManager tags.

        Returns: event array, event ids dictionary (event_id -> tag description).
        """
        ans = self.mne_annotations()
        unique_descs = numpy.unique(ans.description)
        event_id = {}
        for desc_id, desc in enumerate(unique_descs, start=1):
            event_id[desc] = desc_id

        sampling_rate = float(self.get_param('sampling_frequency'))

        # first column - onset in samples
        # second - read only in few special cases, so we can leave it as zeros
        # third - event id
        events = numpy.zeros((len(ans.onset), 3), dtype=int)
        onset_s = numpy.round(ans.onset * sampling_rate)
        events[:, 0] = onset_s

        for desc_n, desc in enumerate(ans.description):
            events[desc_n, 2] = event_id[desc]
        return events, event_id

    def _set_mne_tags(self, raw):
        add_stim_chnl(raw)
        ans = self.mne_annotations()
        events, _ = self.mne_events()
        raw.annotations = ans
        raw.add_events(events)

# -*- coding: utf-8 -*-
# Copyright (c) 2016-2018 Braintech Sp. z o.o. [Ltd.] <http://www.braintech.pl>
# All rights reserved.

"""Mixin for SmartTagsManager to create MNE.Epochs objects."""
import mne
import numpy
from ..read_manager import ReadManager

from .utils import requires_mne


class SmartTagManagerMNEMixin:
    """Mixin for ReadManager containing MNE conversions."""

    @requires_mne
    def get_mne_epochs(self, p_tag_type=None, p_from=None, p_len=None, p_func=None, event_descs=None,
                       channel_types=None):
        """Get MNE.Epochs of given tag type.

        You can filter tags by:
        :param p_tag_type: string - filters tag name, can be None for any.
        :param p_from: float - only use tags after this second of signal, can be None for all.
        :param p_len: float - use tags from time: p_from until p_from + p_len, if None from p_from until end of signal.
        :p_func: callable, or list of callables func(tag_dict) -> bool - custom tag filtering function.
            Takes a tag in dictionary format and returns True if tag meets criteria to be used, False if not.
            If list of functions, then returned MNE Object will have epochs with according event_ids set.
            Be warned - all parameters in tag descriptions are of type str. Example function:

                def func1(tag):
                    try:
                        return tag['desc']['value'] == '1'
                    except:
                        return False

            Tags only will be selected when in their description there is a parameter named "value" with value "1".

        :param event_descs: Optional - list of strings - same length as p_func list - event_id descriptions.

        :param: channel_types optional list of strings with channel types:
           ‘ecg’, ‘bio’, ‘stim’, ‘eog’, ‘misc’, ‘seeg’, ‘ecog’, ‘mag’, ‘eeg’, ‘ref_meg’, ‘grad’, ‘emg’, ‘hbr’ or ‘hbo’
           if None channels types will be selected heuristically.
        """
        if p_func is not None and event_descs is not None:
            assert len(p_func) == len(event_descs)

        try:
            p_func[0]
        except TypeError:
            p_func = [p_func, ]

        if event_descs is None:
            event_descs = [str(i) for i in range(len(p_func))]

        event_ids_mne = {k: v for k, v in zip(event_descs, range(len(p_func)))}

        mne_info = None
        tag_def = None

        all_epochs = []
        events_mne = []

        for tagid, func in enumerate(p_func):
            stags = self.get_smart_tags(p_tag_type=p_tag_type, p_from=p_from, p_len=p_len,
                                        p_func=func)
            for stag in stags:
                events_mne.append([1, 1, tagid])
                data = stag.get_microvolt_samples()
                all_epochs.append(data)

                if mne_info is None:
                    mne_info = stag.get_mne_info(channel_types)
                if tag_def is None:
                    tag_def = stag._tag_def

        start_offset = tag_def.start_offset

        if len(all_epochs) < 1:
            raise Exception('No epochs found meeting p_func criteria')

        events_mne_np = numpy.array(events_mne)
        # Event timings are not relevant anymore, but must be unique
        events_mne_np[:, 0] = numpy.arange(0, len(all_epochs), 1)

        all_epochs_np = numpy.stack(all_epochs) * 1e-6  # to Volts

        e_mne = mne.EpochsArray(all_epochs_np,
                                mne_info,
                                tmin=start_offset,
                                events=events_mne_np,
                                event_id=event_ids_mne)
        return e_mne

    @classmethod
    @requires_mne
    def get_smart_tags_from_mne_epochs(cls, epochs):
        """Generate list of small ReadManagers from epochs.

        This can be used in the same way as result of SmartTagsManager.get_smart_tags().
        """
        tags = []
        for e in epochs:
            # mne epochs when iterating return data
            data = e * 1e6
            tags.append(ReadManager._rm_from_mne_data(data, epochs.info, ))
        return tags

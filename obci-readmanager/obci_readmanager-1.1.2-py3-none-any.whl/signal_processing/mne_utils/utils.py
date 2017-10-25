# -*- coding: utf-8 -*-
# Copyright (c) 2016-2018 Braintech Sp. z o.o. [Ltd.] <http://www.braintech.pl>
# All rights reserved.

"""Misc utils needed for obci-MNE conversion."""
try:
    import mne
except ImportError:
    mne = None


def requires_mne(func):
    """Make sure that mne is loaded, point user to installing."""
    def wrapper(*args, **kwargs):
        if mne is None:
            raise Exception("You have no MNE installed, to install visit http://martinos.org/mne/stable/\n"
                            "Alternatively you can try running:\n"
                            "pip3 install --user mne")
        return func(*args, **kwargs)
    return wrapper


def chtype_heuristic(chname):
    """Channel type heuristic.

    Returns channel type string for given channel name.
    :param: chname
    """
    montage = mne.channels.read_montage('standard_1005')
    norm_names = [i.lower() for i in montage.ch_names]
    if chname.lower() in norm_names:
        return 'eeg'

    if 'emg' in chname.lower():
        return 'emg'

    if 'eog' in chname.lower():
        return 'eog'

    return 'misc'

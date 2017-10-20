# Authors: Jaakko Leppakangas <jaeilepp@student.jyu.fi>
#
# License: BSD 3 clause

from datetime import datetime
import os.path as op
import warnings

from nose.tools import assert_raises, assert_true
from numpy.testing import (assert_equal, assert_array_equal,
                           assert_array_almost_equal, assert_allclose)

import numpy as np

from mne import create_info, Epochs
from mne.utils import run_tests_if_main
from mne.io import read_raw_fif, RawArray, concatenate_raws
from mne.annotations import Annotations, _sync_onset
from mne.datasets import testing

data_dir = op.join(testing.data_path(download=False), 'MEG', 'sample')
fif_fname = op.join(data_dir, 'sample_audvis_trunc_raw.fif')


@testing.requires_testing_data
def test_annotations():
    """Test annotation class."""
    raw = read_raw_fif(fif_fname)
    onset = np.array(range(10))
    duration = np.ones(10)
    description = np.repeat('test', 10)
    dt = datetime.utcnow()
    meas_date = raw.info['meas_date']
    # Test time shifts.
    for orig_time in [None, dt, meas_date[0], meas_date]:
        annot = Annotations(onset, duration, description, orig_time)

    assert_raises(ValueError, Annotations, onset, duration, description[:9])
    assert_raises(ValueError, Annotations, [onset, 1], duration, description)
    assert_raises(ValueError, Annotations, onset, [duration, 1], description)

    # Test combining annotations with concatenate_raws
    raw2 = raw.copy()
    orig_time = (meas_date[0] + meas_date[1] * 0.000001 +
                 raw2.first_samp / raw2.info['sfreq'])
    annot = Annotations(onset, duration, description, orig_time)
    assert_true(' segments' in repr(annot))
    raw2.annotations = annot
    assert_array_equal(raw2.annotations.onset, onset)
    concatenate_raws([raw, raw2])
    raw.annotations.delete(-1)  # remove boundary annotations
    raw.annotations.delete(-1)
    assert_array_almost_equal(onset + 20., raw.annotations.onset, decimal=2)
    assert_array_equal(annot.duration, raw.annotations.duration)
    assert_array_equal(raw.annotations.description, np.repeat('test', 10))

    # Test combining with RawArray and orig_times
    data = np.random.randn(2, 1000) * 10e-12
    sfreq = 100.
    info = create_info(ch_names=['MEG1', 'MEG2'], ch_types=['grad'] * 2,
                       sfreq=sfreq)
    info['meas_date'] = 0
    raws = []
    for i, fs in enumerate([12300, 100, 12]):
        raw = RawArray(data.copy(), info, first_samp=fs)
        ants = Annotations([1., 2.], [.5, .5], 'x', fs / sfreq)
        raw.annotations = ants
        raws.append(raw)
    raw = RawArray(data.copy(), info)
    raw.annotations = Annotations([1.], [.5], 'x', None)
    raws.append(raw)
    raw = concatenate_raws(raws)
    boundary_idx = np.where(raw.annotations.description == 'BAD boundary')[0]
    assert_equal(len(boundary_idx), 3)
    raw.annotations.delete(boundary_idx)
    boundary_idx = np.where(raw.annotations.description == 'EDGE boundary')[0]
    assert_equal(len(boundary_idx), 3)
    raw.annotations.delete(boundary_idx)
    assert_array_equal(raw.annotations.onset, [1., 2., 11., 12., 21., 22.,
                                               31.])
    raw.annotations.delete(2)
    assert_array_equal(raw.annotations.onset, [1., 2., 12., 21., 22., 31.])
    raw.annotations.append(5, 1.5, 'y')
    assert_array_equal(raw.annotations.onset, [1., 2., 12., 21., 22., 31., 5])
    assert_array_equal(raw.annotations.duration, [.5, .5, .5, .5, .5, .5, 1.5])
    assert_array_equal(raw.annotations.description, ['x', 'x', 'x', 'x', 'x',
                                                     'x', 'y'])

    # Test concatenating annotations with and without orig_time.
    raw = read_raw_fif(fif_fname)
    last_time = raw.last_samp / raw.info['sfreq']
    raw2 = raw.copy()
    raw.annotations = Annotations([45.], [3], 'test', raw.info['meas_date'])
    raw2.annotations = Annotations([2.], [3], 'BAD', None)
    raw = concatenate_raws([raw, raw2])
    raw.annotations.delete(-1)  # remove boundary annotations
    raw.annotations.delete(-1)
    assert_array_almost_equal(raw.annotations.onset, [45., 2. + last_time],
                              decimal=2)


@testing.requires_testing_data
def test_raw_reject():
    """Test raw data getter with annotation reject."""
    info = create_info(['a', 'b', 'c', 'd', 'e'], 100, ch_types='eeg')
    raw = RawArray(np.ones((5, 15000)), info)
    with warnings.catch_warnings(record=True):  # one outside range
        raw.annotations = Annotations([2, 100, 105, 148], [2, 8, 5, 8], 'BAD')
    data = raw.get_data([0, 1, 3, 4], 100, 11200, 'omit')
    assert_array_equal(data.shape, (4, 9900))

    # with orig_time and complete overlap
    raw = read_raw_fif(fif_fname)
    raw.annotations = Annotations([44, 47, 48], [1, 3, 1], 'BAD',
                                  raw.info['meas_date'])
    data, times = raw.get_data(range(10), 0, 6000, 'omit', True)
    assert_array_equal(data.shape, (10, 4799))
    assert_equal(times[-1], raw.times[5999])
    assert_array_equal(data[:, -100:], raw[:10, 5900:6000][0])

    data, times = raw.get_data(range(10), 0, 6000, 'NaN', True)
    assert_array_equal(data.shape, (10, 6000))
    assert_equal(times[-1], raw.times[5999])
    assert_true(np.isnan(data[:, 313:613]).all())  # 1s -2s
    assert_true(not np.isnan(data[:, 614].any()))
    assert_array_equal(data[:, -100:], raw[:10, 5900:6000][0])
    assert_array_equal(raw.get_data(), raw[:][0])

    # Test _sync_onset
    times = [10, -88, 190]
    onsets = _sync_onset(raw, times)
    assert_array_almost_equal(onsets, times - raw.first_samp /
                              raw.info['sfreq'])
    assert_array_almost_equal(times, _sync_onset(raw, onsets, True))


def test_annotation_filtering():
    """Test that annotations work properly with filtering."""
    # Create data with just a DC component
    data = np.ones((1, 1000))
    info = create_info(1, 1000., 'eeg')
    raws = [RawArray(data * (ii + 1), info) for ii in range(4)]
    kwargs_pass = dict(l_freq=None, h_freq=50., fir_design='firwin')
    kwargs_stop = dict(l_freq=50., h_freq=None, fir_design='firwin')
    # lowpass filter, which should not modify the data
    raws_pass = [raw.copy().filter(**kwargs_pass) for raw in raws]
    # highpass filter, which should zero it out
    raws_stop = [raw.copy().filter(**kwargs_stop) for raw in raws]
    # concat the original and the filtered segments
    raws_concat = concatenate_raws([raw.copy() for raw in raws])
    raws_zero = raws_concat.copy().apply_function(lambda x: x * 0)
    raws_pass_concat = concatenate_raws(raws_pass)
    raws_stop_concat = concatenate_raws(raws_stop)
    # make sure we did something reasonable with our individual-file filtering
    assert_allclose(raws_concat[0][0], raws_pass_concat[0][0], atol=1e-14)
    assert_allclose(raws_zero[0][0], raws_stop_concat[0][0], atol=1e-14)
    # ensure that our Annotations cut up the filtering properly
    raws_concat_pass = raws_concat.copy().filter(skip_by_annotation='edge',
                                                 **kwargs_pass)
    assert_allclose(raws_concat[0][0], raws_concat_pass[0][0], atol=1e-14)
    raws_concat_stop = raws_concat.copy().filter(skip_by_annotation='edge',
                                                 **kwargs_stop)
    assert_allclose(raws_zero[0][0], raws_concat_stop[0][0], atol=1e-14)
    # one last test: let's cut out a section entirely:
    # here the 1-3 second window should be skipped
    raw = raws_concat.copy()
    raw.annotations.append(1., 2., 'foo')
    raw.filter(l_freq=50., h_freq=None, fir_design='firwin',
               skip_by_annotation='foo')
    # our filter will zero out anything not skipped:
    mask = np.concatenate((np.zeros(1000), np.ones(2000), np.zeros(1000)))
    expected_data = raws_concat[0][0][0] * mask
    assert_allclose(raw[0][0][0], expected_data, atol=1e-14)


def test_annotation_omit():
    """Test raw.get_data with annotations."""
    data = np.concatenate([np.ones((1, 1000)), 2 * np.ones((1, 1000))], -1)
    info = create_info(1, 1000., 'eeg')
    raw = RawArray(data, info)
    raw.annotations = Annotations([0.5], [1], ['bad'])
    expected = raw[0][0]
    assert_allclose(raw.get_data(reject_by_annotation=None), expected)
    # nan
    expected[0, 500:1500] = np.nan
    assert_allclose(raw.get_data(reject_by_annotation='nan'), expected)
    got = np.concatenate([raw.get_data(start=start, stop=stop,
                                       reject_by_annotation='nan')
                          for start, stop in ((0, 1000), (1000, 2000))], -1)
    assert_allclose(got, expected)
    # omit
    expected = expected[:, np.isfinite(expected[0])]
    assert_allclose(raw.get_data(reject_by_annotation='omit'), expected)
    got = np.concatenate([raw.get_data(start=start, stop=stop,
                                       reject_by_annotation='omit')
                          for start, stop in ((0, 1000), (1000, 2000))], -1)
    assert_allclose(got, expected)
    assert_raises(ValueError, raw.get_data, reject_by_annotation='foo')


def test_annotation_epoching():
    """Test that annotations work properly with concatenated edges."""
    # Create data with just a DC component
    data = np.ones((1, 1000))
    info = create_info(1, 1000., 'eeg')
    raw = concatenate_raws([RawArray(data, info) for ii in range(3)])
    events = np.array([[a, 0, 1] for a in [0, 500, 1000, 1500, 2000]])
    epochs = Epochs(raw, events, tmin=0, tmax=0.999, baseline=None,
                    preload=True)  # 1000 samples long
    assert_equal(len(epochs.drop_log), len(events))
    assert_equal(len(epochs), 3)
    assert_equal([0, 2, 4], epochs.selection)


run_tests_if_main()

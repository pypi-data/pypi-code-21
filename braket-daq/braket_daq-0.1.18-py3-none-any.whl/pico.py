#! /usr/bin/env python

from contextlib import contextmanager
from functools import lru_cache
import itertools
import re
import sys
import pathlib
from io import StringIO

import numpy as np
import pandas as pd
import xarray as xr


class PrintCatcher(object):  # pragma: no cover  This is a testing utility
    def __init__(self, stream='stdout'):
        self.text = ''
        if stream not in {'stdout', 'stderr'}:
            raise ValueError('stream must be either "stdout" or "stderr"')
        self.stream = stream

    def write(self, text):
        self.text += text

    def flush(self):
        pass

    def __enter__(self):
        if self.stream == 'stdout':
            sys.stdout = self
        else:
            sys.stderr = self
        return self

    def __exit__(self, *args):
        if self.stream == 'stdout':
            sys.stdout = sys.__stdout__
        else:
            sys.stderr = sys.__stderr__


class CSV:
    def __init__(
            self, file_name, nrows=None, standardize=True,
            max_sample_freq=1e6, **channel_names):
        """
        This class provides visualization capabilities for picoscope csv files


        :type file_name: str
        :param file_name: The csv file name

        :type nrows:  int
        :param nrows: Only read this many records from the csv file

        :type standardize: Bool
        :param standardize: Convert everything to SI units (default=True)

        :type max_sample_freq: float
        :param max_sample_freq: Downsample if freq exceeds max_sample_freq (hz)

        :type channel_names: str *kwargs
        :param channel_names: channel name mappings like a='primary', b='secondary'

        """
        is_csv = bool(re.match(r'.*\.csv$', file_name))
        if not is_csv:
            raise ValueError('You can only supply csv files')

        self.file_name = file_name

        if set(channel_names.keys()) - set('abcd'):
            raise ValueError('\n\nCan only supply names for channels labeled "a", "b", "c", or "d"')
        self._conversions = {
            'ms': (.001, 's'),
            'mV': (.001, 'v'),
        }

        self.max_sample_freq = max_sample_freq
        self._channel_names = channel_names
        self._standardize = standardize
        self._units = None
        self._sample_freq = None
        self.df = self.load(nrows)

    @property
    def sample_freq(self):
        """
        The sample frequency of the loaded dataframe
        """
        return self.get_sample_freq(self.df)

    def get_sample_freq(self, df):
        """
        Returns the sample frequency from a dataframe

        :type df: pandas.DataFrame
        :param df: A pandas dataframe from which to compute sample frequency

        :rtype: float
        :return: Sample frequency in inverse units of the dataframe time units
        """
        sample_time = df.head(1000).iloc[:, 0].diff().median()
        return 1. / sample_time

    @property
    def units(self):
        """
        The units specified for the input csv columns
        """
        if self._units is None:
            with open(self.file_name) as in_file:
                for line_no, line in itertools.islice(enumerate(in_file), 2):
                    if line_no == 1:
                        units_line = line.strip()

            rex_list = [
                re.compile(r'\((\S+)\),\((\S+)\),\((\S+)\),\((\S+)\),\((\S+)\)'),
                re.compile(r'\((\S+)\),\((\S+)\),\((\S+)\),\((\S+)\)'),
                re.compile(r'\((\S+)\),\((\S+)\),\((\S+)\)'),
                re.compile(r'\((\S+)\),\((\S+)\)'),
            ]

            for rex in rex_list:
                m = rex.match(units_line)
                if m:
                    self._units = list(m.groups())
                    break

        return self._units

    @property
    def unit_map(self):
        """
        A dictionary mapping column name to unit name
        """
        return dict(zip(self.channels, self.units))

    @property
    def channels(self):
        """
        A list of channels names
        """
        return list(self.df.columns)

    def _do_standardize(self, df):
        """
        This method standardizes the units of all columns to be in SI

        :type df: pandas.DataFrame
        :param df: A pandas dataframe from which to compute sample frequency
        """
        for ind, (orig_unit, col_name) in enumerate(zip(self.units, df.columns)):
            multiplier, new_unit = self._conversions.get(orig_unit, (None, None))
            if multiplier is not None:
                df.loc[:, col_name] = multiplier * df.loc[:, col_name]
                self._units[ind] = new_unit
        return df

    def _rename_columns(self, df):
        """
        Rename columns to t, a, b, c, d

        :type df: pandas.DataFrame
        :param df: A pandas dataframe for renaming columns
        """
        new_names = {'Time': 't'}
        new_names.update({'Channel {}'.format(s.upper()): s for s in 'abcd'})
        df.rename(columns=new_names, inplace=True)
        return df

    def _customize_names(self, df):
        """
        Customizes column names to those specified by the user

        :type df: pandas.DataFrame
        :param df: A pandas dataframe for renaming columns
        """
        df.rename(columns=self._channel_names, inplace=True)
        return df

    def _down_sample(self, df, delta=None):
        """
        Downsample the supplied dataframe to have a minimum sample time.
        All measurements are averaged over the mininum sample time

        :type df: pandas.DataFrame
        :param df: A pandas dataframe for renaming columns

        :type delta: float
        :param delta: The minimum sample time in the same time uints as df
        """
        if delta is None:
            return df
        else:
            df.loc[:, 't'] = delta * (df.t // delta)
            dfg = df.groupby(by='t').mean().reset_index()
            return dfg

    def load(self, nrows=None):
        """
        Load data optionally limiting to nrows records

        :type nrows: int
        :param df: The maxinumum number of rows to load (defaults to all)
        """
        # remove bad characters from file buffer
        bad_chars = ['-∞', '∞']
        with open(self.file_name) as file:
            contents = file.read()
            for char in bad_chars:
                contents = contents.replace(char, '')

            # create a dataframe from file and fill nans
            df = pd.read_csv(StringIO(contents), dtype=np.float64, skiprows=[1, 2], nrows=nrows)
            df.fillna(method='ffill', inplace=True)

        self._rename_columns(df)
        self._customize_names(df)
        if self._standardize:
            self._do_standardize(df)

        if self.get_sample_freq(df) > self.max_sample_freq:
            df = self._down_sample(df, 1. / self.max_sample_freq)
        return df


class Plotter:
    def __init__(self, frame_or_file, max_sample_freq=1e6):
        self.max_sample_freq = max_sample_freq
        self.df = self.load(frame_or_file)
        # weird import location because holoviews is really heavy and I don't
        #  want it loaded unless I need it
        # continuum stuff has annoying deprecation warnings so blank them with
        #  stderr catcher
        with PrintCatcher('stderr'):
            import datashader as ds
            import holoviews as hv
            from holoviews.operation.datashader import datashade
            hv.extension('bokeh')
            from pandashells.lib.lomb_scargle_lib import lomb_scargle
        self.ds = ds
        self.hv = hv
        self.datashade = datashade
        self.lomb_scargle = lomb_scargle

        self.channels = [c for c in self.df.columns if not c == 't']
        self.unit_map = {'t': 'seconds'}
        self.unit_map.update({chan: 'volts' for chan in self.channels})

    def __str__(self):
        return str(self.channels)

    def __repr__(self):
        return self.__str__()

    def load(self, frame_or_file):
        if isinstance(frame_or_file, pd.DataFrame):
            df = frame_or_file

        elif isinstance(frame_or_file, str):
            file = pathlib.Path(frame_or_file)
            if not file.is_file():
                raise ValueError('File {} does not exist'.format(file.as_posix()))

            if file.suffix == '.csv':
                df = CSV(frame_or_file, max_sample_freq=self.max_sample_freq).df
            elif file.suffix == '.nc':
                data = Data()
                df = data.load(frame_or_file)
            else:
                raise ValueError('File type {} not recognized'.format(file.suffix))
        else:
            raise ValueError('frame_or_file must be either a string or a dataframe')

        return df

    def overlay_curves(self, *curves):
        """
        A utility method for overlaying holoviews curves

        :type curves:  holoviews.Curve
        :param curves: *args hold curves to overlay
        """
        disp = self.hv.Overlay(curves).collate()
        self.hv.util.opts('RGB [width=800 height=400]', disp)
        return disp

    def validate_channels(self, channels):
        if not channels:
            raise ValueError('\n\nYou must specify at least one channel')
        if len(channels) > 2:
            raise ValueError('\n\nYou can plot at most 2 channels for now')

        bad_channels = set(channels) - set(self.channels)
        if bad_channels or not channels:
            raise ValueError('\n\nMust supply channel names from {}'.format(self.channels))

    def plot_time_series(self, *channels, color=None):
        """
        Plot time series for the supplied channel names.

        :type channels: str
        :param channels: *args of channel names
        """
        self.validate_channels(channels)
        time_dim = self.hv.Dimension('time', label='time', unit=self.unit_map['t'])
        if color is None:
            colors = ['blue', 'red', 'green', 'black']
        else:
            colors = [color, color, color, color]

        curves = []
        for ind, channel in enumerate(channels):
            chan_dim = self.hv.Dimension(channel, label=channel, unit=self.unit_map[channel])
            curve = self.hv.Curve((self.df.t, self.df.loc[:, channel]), kdims=[time_dim], vdims=[chan_dim])
            curve = self.datashade(curve, aggregator=self.ds.reductions.any(), cmap=[colors[ind]])

            curves.append(curve)

        return self.overlay_curves(*curves)

    @lru_cache()
    def get_spectrum(self, channel, db=True, normalized=False):

        df = self.lomb_scargle(self.df, 't', channel, freq_order=True)
        if normalized:
            df.loc[:, 'power'] = df.power / df.power.sum()
        if db:
            df.loc[:, 'power'] = 10 * np.log10(df.power)
        return df

    def plot_spectrum(self, channel, color='blue', db=True, normalized=False):
        """
        Plot spectrum for the supplied channel.

        :type channel: str
        :param channel: channel name

        :type db: bool
        :param db: Use dB scale for spectrum power

        :type normalize: bool
        :param normalize: Normalize spectrum so that sum(power) = 1
        """
        self.validate_channels([channel])

        df = self.get_spectrum(channel, db=db, normalized=normalized)
        freq_dim = self.hv.Dimension('freq', label='freq', unit='Hz')

        if db:
            unit = 'db power'
        else:
            unit = 'power'

        chan_dim = self.hv.Dimension(channel, label=channel, unit=unit)
        curve = self.hv.Curve((df.freq, df.power), kdims=[freq_dim], vdims=[chan_dim])
        curve = self.datashade(curve, aggregator=self.ds.reductions.any(), cmap=[color])
        self.hv.util.opts('RGB [width=800 height=400]', curve)
        return curve


class Data:
    CURRENT_VERSION = '1.0.0'

    def __init__(self, bits=14, dtype=None):
        self.version = self.CURRENT_VERSION
        self.bits = bits
        if dtype is None:
            self.dtype = np.int16
        else:
            self.dtype = dtype

        self.meta = {
            '__version__': self.version,
            '__dtype__': self.dtype.__name__,
            '__bits__': self.bits,
        }

    @staticmethod
    @contextmanager
    def dataset(file_or_frame):
        if isinstance(file_or_frame, str):
            dset = xr.open_dataset(file_or_frame)
        elif isinstance(file_or_frame, pd.DataFrame):
            dset = xr.Dataset.from_dataframe(file_or_frame)
        else:
            raise ValueError('Dataset can only be created with file_name or dataframe')

        yield dset
        dset.close()

    def compress_data_frame(self, df):
        # save meta info needed to reconstitute time
        self.meta['__delta_t__'] = delta_t = df.t.diff().median()
        self.meta['__start_index__'] = int(np.round(df.t.iloc[0] / delta_t))

        # no longer need time in the dataframe
        df.drop('t', axis=1, inplace=True)

        #  loop over all other columns saving scale values and transforming to dtype
        for col in df.columns:
            scale = df.loc[:, col].abs().max() / 2 ** self.bits
            self.meta['__scale_{}__'.format(col)] = scale
            df.loc[:, col] = (df.loc[:, col] / scale).round().astype(self.dtype)
        return df

    def csv_to_netcdf(self, csv_file_name, netcdf_file_name, **attrs):
        # store any additional attributes in the meta dict
        self.meta.update(**attrs)

        # load a pico dataframe from the csv file
        df = CSV(csv_file_name).df

        # compress the dataframe and store meta information for reconstitution
        df = self.compress_data_frame(df)

        # create an xarray dataset from the dataframe
        with self.dataset(df) as dset:
            # set the meta information on the array
            dset.attrs = self.meta

            # write to netcdf
            dset.to_netcdf(netcdf_file_name)

    def load_meta(self, netcdf_file_name):
        with self.dataset(netcdf_file_name) as dset:
            meta = dset.attrs
        self.meta = meta
        return meta

    def get_channel_mappings(self):
        allowed_names = {
            'channel_a',
            'channel_b',
            'channel_c',
            'channel_d',
        }
        mappings = {}
        for k, v in self.meta.items():
            if k in allowed_names:
                mappings[k.replace('channel_', '')] = v
        return mappings

    def load(self, netcdf_file_name, channel_mappings=None):
        # load the data into a dataframe and extract the meta
        with self.dataset(netcdf_file_name) as dset:
            self.meta = dset.attrs
            df = dset.to_dataframe()

        # fill the channel mappings
        if channel_mappings is None:
            channel_mappings = self.get_channel_mappings()

        specified_channels = set(channel_mappings.keys())
        allowed_channels = set('abcd')
        bad_channels = specified_channels - allowed_channels
        if bad_channels:
            raise ValueError('Channel names must be taken from {}'.format(allowed_channels))

        # extract the scale mapping for all columns
        rex_scale = re.compile(r'__scale_([a-z])__')
        scales = {}
        for key, val in self.meta.items():
            m = rex_scale.match(key)
            if m:
                col = m.group(1)
                scales[col] = val

        # reconstitute time
        df.insert(0, 't', range(len(df)))
        df.loc[:, 't'] = (self.meta['__start_index__'] + df.t) * self.meta['__delta_t__']

        # scale columns
        for col, scale in scales.items():
            df.loc[:, col] = scale * df.loc[:, col]

        # rename channels
        df.rename(columns=channel_mappings, inplace=True)
        self.df = df
        return df

#!/usr/bin/python

"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

"""

import datetime
import time
import collections
import json
import logging
import os.path
import traceback
import usb
import copy
import gateway_helpers
from configparser import ConfigParser
from gateway_helpers import dt2ms, post_log, \
    round_sig, logger
from scope import IviScopeClient
from base import BaseClient


cfg = ConfigParser()
cfg.read('/etc/gradient_one.cfg')
COMMON_SETTINGS = cfg['common']
CLIENT_SETTINGS = cfg['client']
try:
    TMPDIR = CLIENT_SETTINGS["TMPDIR"]
except:
    TMPDIR = "/tmp"

SENTRY_CLIENT = gateway_helpers.get_sentry()

CLIENT_ID = 'ORIGINAL'
SAMPLE_FILE = 'MDO30121M.txt'
CONFIG_URL = ("https://" + COMMON_SETTINGS['DOMAIN'] + "/testplansummary/" +
              COMMON_SETTINGS['COMPANYNAME'] + '/' +
              COMMON_SETTINGS['HARDWARENAME'])
COMPANYNAME = COMMON_SETTINGS['COMPANYNAME']
HARDWARENAME = COMMON_SETTINGS['HARDWARENAME']
MAX_VALID_MEAS_VAL = 1000000000
BASE_URL = gateway_helpers.BASE_URL
DEFAULT_TEK_CONFIG = {
    "outputs": {
        "impedance": 50,
        "enabled": True
    },
    "output_noise": {
        "enabled": False,
        "percent": 0
    },
    "channels": [{
        "range": 2,
        "offset": 0,
        "enabled": True,
        "coupling": "dc",
        "name": "ch1"
    }, {
        "range": 1,
        "offset": 0,
        "enabled": False,
        "coupling": "dc",
        "name": "ch2"
    }, {
        "range": 1,
        "offset": 0,
        "enabled": False,
        "coupling": "dc",
        "name": "ch3"
    }, {
        "range": 1,
        "offset": 0,
        "enabled": False,
        "coupling": "dc",
        "name": "ch4"
    }],
    "trigger_edge_slope": "positive",
    "trigger": {
        "source": "ch1",
        "type": "edge",
        "coupling": "dc",
        "level": 0.288
    },
    "acquisition": {
        "number_of_points_minimum": 1000,
        "start_time": -4.999999999999996e-06,
        "number_of_envelopes": 0,
        "time_per_record": 9.999999999999999e-06,
        "type": "average",
        "number_of_averages": 512
    },
    "standard_waveform": {
        "dc_offset": 0,
        "symmetry": 50,
        "duty_cycle_high": 50,
        "start_phase": 0,
        "waveform": "square",
        "frequency": 220000,
        "amplitude": 1,
        "pulse_width": 1e-06
    }
}


class Transformer(BaseClient):

    """transforms instructions from the server to instrument commands

    The Transformer will request a instrument instance based on the
    instrument_type given in the configuration and passes the parameters
    to the instrument. After the run, the Transformer reads back the data
    from the instrument to package up for a Transmitter to tranmit to
    the server."""

    def __init__(self, command, instr=None, session=None):
        self.setup = command  # setup attribute to be deprecated
        self.command = command
        self.instr = instr
        self.session = session
        self.dec_factor = 1
        self.command_id = None
        self.trace_dict = {}
        self.timer = gateway_helpers.Timer()
        self.metadata = collections.defaultdict(int)

    def _write_trace_dict(self):
        filename = 'full-trace-%s.json' % self.metadata['result_id']
        trace_file = os.path.join(TMPDIR, filename)
        with open(trace_file, 'w') as f:
            f.write(json.dumps(self.trace_dict))


class IviTransformer(Transformer):

    """transformer for ivi instruments"""

    def __init__(self, command, instrument, session):
        Transformer.__init__(self, command, session=session)
        self.instr = instrument
        self.instr._write("*CLS")
        self.ivi_channels = self.instr.channels


class ScopeTransformer(IviTransformer, IviScopeClient):

    """transformer for oscilloscopes"""

    def __init__(self, command, instrument=None, session=None):
        IviTransformer.__init__(self, command, instrument, session)
        self.trace_dict = {}
        self.channels = []  # for storing channel info by channel
        self.trace_dict['channels'] = self.channels  # store it with other data
        self.command = command
        self.channel_names = [c.name for c in self.ivi_channels]
        self._analog_channel_names = self.instr._analog_channel_name
        self.ch_idx_dict = {
            'ch1': 0,
            'ch2': 1,
            'ch3': 2,
            'ch4': 3,
        }
        self.enabled_list = ['ch1']  # by default, only ch1 enabled
        self.set_adders = 0
        self.exception_count = 0
        self.screenshot_blob_key = ''
        self.g1_measurement_results = collections.defaultdict(int)
        self._horizontal_divisions = 10
        self._vertical_divisions = 10
        dd = collections.defaultdict(str)
        self.ce_dict = collections.defaultdict(lambda: dd)
        self.config_scorecard = {
            'success': [],
            'failure': [],
            'errors': {
                'usb_timeouts': 0,
                'usb_resource_busy': 0,
            },
            'times': {
                'start_to_finish': 0,
                'load_config': 0,
                'fetch_waveform': 0,
                'fetch_measurements': 0,
            }
        }
        self.times = {
            'init': time.clock(),
            'load_config_start': 0,
            'load_config_end': 0,
            'fetch_measurements_start': 0,
            'fetch_measurements_end': 0,
            'complete': 0,
        }
        self.config = collections.defaultdict(lambda: {})
        self.config.update(command['info'])
        if command['category'] == 'Capture':
            logger.debug("creating cloud capture transformer")
            self.capture_mode = True
        else:
            logger.debug("creating user-configured transformer")
            self.capture_mode = False
            try:
                if self.command['label'] == 'grl_test':
                    self.ce_dict.update(DEFAULT_TEK_CONFIG)
                elif self.command['category'] == 'Config':
                    ce = command['info']['config_excerpt']
                    ce = self.validate_config_excerpt(ce)
                    self.ce_dict.update(ce)
                else:
                    self.ce_dict.update(command['info'])
            except Exception:
                logger.debug("Exception in loading Config Excerpt")
                logger.debug(traceback.format_exc())
        self.command_id = str(self.command['id'])
        base_meas = [
            #      {
            #          'ivi_name': 'rise_time',
            #          'display_name': 'Rise Time',
            #          'units': 's',
            #      },
            #      {
            #          'ivi_name': 'fall_time',
            #          'display_name': 'Fall Time',
            #          'units': 's',
            #     },
            {
                'ivi_name': 'frequency',
                'display_name': 'Frequency',
                'units': 'Hz',
            },
            #     {
            #         'ivi_name': 'period',
            #         'display_name': 'Period',
            #         'units': 's',
            #     },
            #     {
            #         'ivi_name': 'voltage_rms',
            #         'display_name': 'Voltage RMS',
            #         'units': 'V',
            #     },
            #     {
            #         'ivi_name': 'voltage_peak_to_peak',
            #         'display_name': 'Voltage Peak to Peak',
            #         'units': 'V',
            #     },
            #     {
            #         'ivi_name': 'voltage_max',
            #         'display_name': 'Voltage Max',
            #         'units': 'V',
            #     },
            #     {
            #         'ivi_name': 'voltage_min',
            #         'display_name': 'Voltage Min',
            #         'units': 'V',
            #     },
            #     {
            #         'ivi_name': 'voltage_high',
            #         'display_name': 'Voltage High',
            #         'units': 'V',
            #     },
            #     {
            #         'ivi_name': 'voltage_low',
            #         'display_name': 'Voltage Low',
            #         'units': 'V',
            #     },
            #     {
            #         'ivi_name': 'voltage_average',
            #         'display_name': 'Voltage Average',
            #         'units': 'V',
            #     },
            #     {
            #         'ivi_name': 'width_negative',
            #         'display_name': 'Width Negative',
            #         'units': 's',
            #     },
            #     {
            #         'ivi_name': 'width_positive',
            #         'display_name': 'Width Positive',
            #         'units': 's',
            #     },
            #     {
            #         'ivi_name': 'duty_cycle_negative',
            #         'display_name': 'Duty Cycle Negative',
            #         'units': 's',
            #     },
            #     {
            #         'ivi_name': 'duty_cycle_positive',
            #         'display_name': 'Duty Cycle Positive',
            #         'units': 's',
            #     },
            #     {
            #         'ivi_name': 'amplitude',
            #         'display_name': 'Amplititude',
            #         'units': 'V',
            #     },
            #     {
            #          'ivi_name': 'voltage_cycle_rms',
            #          'display_name': 'Voltage Cycle RMS',
            #          'units': 'V',
            #     },
        ]
        self.meas_list = []
        self.meas_list.extend(base_meas)
        if not cfg.getboolean('client', 'SIMULATED'):
            if self.command['info']['instrument_type'] == 'TektronixMSO5204B':
                specific_meas = [
                    {
                        'ivi_name': 'voltage_cycle_average',
                        'display_name': 'Voltage Cycle Average',
                        'units': 'V',
                    },
                    {
                        'ivi_name': 'overshoot_negative',
                        'display_name': 'Overshoot Negative',
                        'units': 'V',
                    },
                    {
                        'ivi_name': 'overshoot_positive',
                        'display_name': 'Overshoot Positive',
                        'units': 'V',
                    },
                ]
                self.meas_list.extend(specific_meas)

            elif self.command['info']['instrument_type'] == 'RigolMSO2302A':
                self.meas_list.append({
                    'ivi_name': 'overshoot',
                    'display_name': 'Overshoot',
                    'units': 'V',
                })
            elif self.command['info']['instrument_type'] == 'RigolDS1054Z':
                self.meas_list.append({
                    'ivi_name': 'overshoot',
                    'display_name': 'Overshoot',
                    'units': 'V',
                })
        self.test_plan = False
        self.acq_dict = {
            'time_per_record': '',
            'number_of_points_minimum': '',
            'type': '',
            'start_time': '',
            'number_of_averages': '',
            'number_of_envelopes': '',
            'record_length': '',
        }

        if cfg.getboolean('client', 'SIMULATED'):
            self.ce_dict['enabled_list'] = self.enabled_list
        logger.debug("ce_dict after init: %s" % self.ce_dict)
        if 'channels' not in self.ce_dict:
            # if empty, initialize with names in self._analog_channel_names:
            self.ce_dict['channels'] = []
            for ch_name in self._analog_channel_names:
                self.ce_dict['channels'].append({'name': ch_name})
        try:
            logger.debug("trying to get channels object")
            self.ivi_channels = self.instr.channels
        except Exception:
            logger.debug("EXCEPTION: unabled to get channels obj", trace=True)
            self.ivi_channels = None
        self.logger = gateway_helpers.logger
        self.first_slice = None
        self.time_step = None
        self.waveform_length = 0
        self.slice_length = 0
        self.trace_dict['channels'] = self.channels
        self.channel_settings = ['range', 'offset', 'position', 'coupling']
        self.category = 'Oscilloscope'
        self.device_under_test = ''
        # end __init__

    def set_timebase(self, timebase_dict):
        for key in timebase_dict:
            self.set_adders += 1
            self._setinstr_with_tries(self.instr.timebase, key,
                                      timebase_dict[key], label='timebase_',
                                      tries=3)

    def load_config(self):
        logger.debug("loading config")
        self.times['load_config_start'] = time.clock()
        if 'info' in self.config and self.config['info'] is not None:
            if 'raw_setup' in self.config['info']:
                self.load_raw_setup()
                time.sleep(1)

        if 'acquisition' in self.ce_dict:
            self._set_acquisition(self.ce_dict['acquisition'])
        if 'trigger' in self.ce_dict:
            self.set_trigger(self.ce_dict['trigger'])
        self.set_channels()
        self.load_special_config_fields()
        self.times['load_config_end'] = time.clock()
        return True

    def load_special_config_fields(self):
        pass

    def load_special_fields(self):
        if 'timebase' in self.ce_dict:
            self.set_timebase(self.ce_dict['timebase'])
        try:
            afg_enabled = self.ce_dict['outputs']['enabled']
            logger.debug("afg_enabled is: %s" % afg_enabled)
        except Exception:
            logger.debug("afg_enabled exception, setting False")
            afg_enabled = False
        if afg_enabled:
            try:
                self.set_outputs(self.ce_dict['outputs'])
                self.set_standard_waveform(self.ce_dict['standard_waveform'])
            except:
                logging.warning("AFG Enabled, but exception setting output")

    def check_any_channel_enabled(self):
        """Checks if any channel is enabled. If none, return False"""
        channels_enabled = []
        for ch in self._analog_channel_names:
            if self.instr.channels[self.ch_idx_dict[ch]].enabled:
                channels_enabled.append(ch)
        if channels_enabled:
            return True
        else:
            logger.warning('No Channels Enabled')
            return False

    def _validate_acq_dict(self, acq_dict):
        if 'record_length' in acq_dict:
            del acq_dict['record_length']
        logger.debug("setting acquisition: " + str(acq_dict))
        try:
            if acq_dict['type'] != 'average':
                if 'number_of_averages' in acq_dict:
                    del acq_dict['number_of_averages']
            if acq_dict['type'] != 'envelope':
                if 'number_of_envelopes' in acq_dict:
                    del acq_dict['number_of_envelopes']
        except Exception as e:
            logger.debug(e, exc_info=True)

    def _set_acquisition(self, acq_dict):
        self._validate_acq_dict(acq_dict)
        for key in acq_dict:
            self.set_adders += 1
            self._setinstr_with_tries(self.instr.acquisition, key,
                                      acq_dict[key], label='acquisition_',
                                      tries=3)

    def set_trigger(self, trigger_dict):
        logger.debug("setting trigger")
        trigger = self.instr.trigger
        for key in trigger_dict:
            self._setinstr(trigger, key, trigger_dict[key], label='trigger_')

        if trigger_dict['type'] == 'edge':
            try:
                value = self.ce_dict['trigger_edge_slope']
                trigger.edge.slope = value
                self.config_scorecard['success'].append('trigger_edge_slope')
            except Exception:
                logger.debug("failed to set edge slope with %s" % value)
                self.config_scorecard['failure'].append('trigger_edge_slope')

    def set_standard_waveform(self, waveform_dict, index=0):
        logger.debug("set standard_waveform")
        standard_waveform = self.instr.outputs[index].standard_waveform
        if not standard_waveform:
            logger.debug("no standard_waveform to set")
            logger.debug("outputs[0] dir: %s" % dir(self.instr.outputs[0]))
            return False

        for key in waveform_dict:
            self._setinstr(standard_waveform, key, waveform_dict[key],
                           label='standard_waveform_')
        return True

    def set_outputs(self, output_dict, index=0):
        logger.debug("set outputs")
        output = self.instr.outputs[index]
        for key in output_dict:
            self._setinstr(output, key, output_dict[key], label='output_')
        try:
            output.noise.enabled = self.ce_dict['output_noise']['enabled']
            if output.noise.enabled:
                output.noise.percent = int(
                    self.ce_dict['output_noise']['percent'])
        except Exception:
            logger.debug("failed to set output noise")
            logger.debug(traceback.format_exc())

    def set_channels(self):
        """Sets the ivi channel data with values from the config

        ivi_channels refers to the ivi intrument.
        The method iterates over the channels in the config excerpt,
        aka the ce_dict, and assigns the channel data to the ivi
        channel object

        This does NOT set the Transformer 'channels' attribute as
        that refers to the channel data collected from the instrument
        rather than the data sent.
        """
        if not isinstance(self.ce_dict['channels'], list):
            logger.warning("set_channels() channels needs to be a list!")
            return
        logger.debug("set channels with ce_dict:%s" % self.ce_dict)
        if not self.ivi_channels:
            self.ivi_channels = self.instr.channels
        for channel in self.ce_dict['channels']:
            if not isinstance(channel, dict):
                logger.warning("Unexpected type for channel %s" % channel)
                continue
            enabled = channel['enabled']
            channel_idx = self.ch_idx_dict[channel['name']]
            logger.debug("%s enabled: %s" % (channel['name'], enabled))
            try:
                self.ivi_channels[channel_idx].enabled = enabled
            except Exception as e:
                logger.debug("exception in setting channel enabled: %s" % e)
            for setting in self.channel_settings:
                if setting not in channel:
                    continue
                self._setinstr(self.instr.channels[channel_idx], setting,
                               channel[setting])

    def _set_enabled_list(self):
        self.enabled_list = []  # resets enabled list
        if cfg.getboolean('client', 'SIMULATED'):
            self.enabled_list = ['ch1']
            return
        for ch in self._analog_channel_names:
            channel_idx = self.ch_idx_dict[ch]
            if self.instr.channels[channel_idx].enabled:
                self.enabled_list.append(ch)
        if self.capture_mode:
            for ch in self.enabled_list:
                channel = collections.defaultdict(int)
                channel['name'] = ch
                channel['enabled'] = True
                self._update_channels(self.ce_dict['channels'], channel)

    def _update_channels(self, channels, channel_data):
        """Updates the channels with the data in channel_data

        Checks for a matching channel in channels according to
        the name of the channel. If found, updates the channel.
        If not found, the channel_data is appended to channels.
        """
        new_channel_flag = True
        # the name key is required for channel data
        if 'name' not in channel_data:
            return
        for channel in channels:
            if 'name' in channel and channel['name'] == channel_data['name']:
                channel.update(channel_data)
                new_channel_flag = False
        # If it's a new channel, append the channel data
        if new_channel_flag:
            channels.append(channel_data)

    def check_commands_completed(self):
        r = self.instr._ask("*ESR?")
        self.logger.debug("*ESR response: %s" % r)
        # r = self.instr._ask("allev?")
        # self.logger.info("allev? response: %s" % r)

    def check_instrument_ready(self):
        """Checks if instrument is ready to run a new command

        Assumes the instrument is 'busy'. Method asks the instrument
        up to 10 times if the instrument is busy. If the ask() returns
        '0' then the instrument is ready to do something else and this
        method will return True. If after 10 tries it still is not
        returning '0' or if there is some exception then this method
        returns False.
        """
        ready = False
        try:
            for i in range(10):
                self.timer.set_timeout(3)
                busy = self.instr._ask('busy?')
                self.timer.clear_timeout()
                if busy == '0':
                    ready = True
                    break
                time.sleep(0.5)
        except Exception as e:
            logger.warning("Exception checking busy status %s" % e)
            self.timer.clear_timeout()  # in case e was before clear
        finally:
            logger.info("Instrument ready? %s" % ready)
            return ready

    def fetch_measurements(self):
        """Fetches trace, metadata, screenshot, and measurements"""
        logger.debug("fetching measurements")
        self.times['fetch_measurements_start'] = time.clock()
        self._set_enabled_list()
        self.time_step = 0.000001
        self.slice_dict = collections.defaultdict(int)
        self.first_slice = collections.defaultdict(int)
        self.trace_dict['start_tse'] = int(dt2ms(datetime.datetime.now()))
        logger.debug("enabled_list: %s" % self.enabled_list)

        # check to return early if instrument is not ready
        if not self.check_instrument_ready():
            return {}

        # Fetch the waveform for each channel enabled
        for ch in self.enabled_list:
            logger.info("Fetching waveform for %s" % ch)
            self._fetch_waveform(ch)

        # Write the dictionary of trace data to file
        self._write_trace_dict()

        # intialize the metadata from channels after waveform fetch
        self.metadata = self._get_metadata(channels=self.channels)
        self.metadata.update(self.get_instrument_settings())

        # Make quick post for first feedback
        self._quick_post_results()

        # Grab a screenshot from the instrument
        self._grab_and_post_screenshot()

        # Run measurements on each channel
        self._fetch_waveform_measurements()
        self.times['fetch_measurements_end'] = time.clock()
        return self.trace_dict

    def _fetch_waveform(self, channel_name):
        """Gets the waveform data from the instrument

        This is the method that actually fetches the data from the
        ivi channel instance for the waveform and channel metadata
        for a given trace.

        This is the method that intializes the channel for the
        transformers channels list for storing the data collected
        for each channel enabled on the scope.
        """
        self.check_commands_completed()  # check if ready
        try:
            channel_idx = self.ch_idx_dict[channel_name]
            ivi_channel = self.instr.channels[channel_idx]
            waveform = list(ivi_channel.measurement.fetch_waveform())
            self.waveform_length = len(waveform)
            logger.debug("waveform length for %s: %s" %
                         (channel_name, self.waveform_length))
            time_step = waveform[1][0] - waveform[0][0]
            voltage_list = self.get_voltage_list(waveform)
            slice_list = self.get_slice_list(voltage_list)
            self.slice_dict[channel_name] = slice_list
            self.first_slice[channel_name] = slice_list[0]
            self.check_commands_completed()
            channel_data = {}
            channel_data = {
                'name': channel_name,
                'y_values': voltage_list,
                'time_step': time_step,
                'start_time': waveform[0][0],
                'end_time': waveform[-1][0],
                'enabled': True,
            }

            # collect channel metadata for plotting
            if hasattr(ivi_channel, 'trigger_level'):
                channel_data['trigger_level'] = ivi_channel.trigger_level
            try:
                channel_data['range'] = ivi_channel.range
                channel_data['coupling'] = ivi_channel.coupling
                channel_data['offset'] = ivi_channel.offset
                channel_data['scale'] = ivi_channel.scale
                # index here is the ivi index number for the channel
                channel_data['index'] = self.ch_idx_dict[channel_name]
            except Exception as e:
                logger.warning(e, exc_info=True)
            if hasattr(ivi_channel, 'position'):
                try:
                    channel_data['position'] = ivi_channel.position
                except Exception as e:
                    logger.warning(e, exc_info=True)
            # update current channels list
            self._update_channels(self.channels, channel_data)
            self.time_step = time_step  # migrate towards ch specific
        except Exception:
            self.logger.warning("failed to fetch waveform for: %s"
                                % channel_name, exc_info=True)

    def _fetch_waveform_measurements(self):
        """Fetches measurments about the waveform

        Note for emphasis: Measurements in this case refers to the
        ivi measurements about the waveform and NOT the waveform
        itself and NOT calculations GradientOne performs on the
        waveform.
        """
        self.check_commands_completed()
        logger.debug("fetching waveform measurements")
        if not self.ivi_channels:
            self.ivi_channels = self.instr.channels
        for channel in self.metadata['channels']:
            ch_idx = self.ch_idx_dict[channel['name']]
            ivi_channel = self.ivi_channels[ch_idx]
            channel['waveform_measurements_valid'] = True  # starts off valid
            for meas in self.meas_list:
                # Skip is simulated (meas_list should be empty anyway)
                if cfg.getboolean('client', 'SIMULATED'):
                    continue
                instrument = ivi_channel.measurement
                val = ''
                try:
                    ivi_name = meas['ivi_name']
                    val = instrument.fetch_waveform_measurement(ivi_name)
                    if val == 'measurement error':
                        meas['value'] == 'N/A'
                    elif val > MAX_VALID_MEAS_VAL:
                        channel['waveform_measurements_valid'] = False
                        meas['value'] = MAX_VALID_MEAS_VAL
                    else:
                        meas['value'] = val
                    self.check_commands_completed()
                except Exception:
                    logger.debug("measurement exception %s" % ivi_name,
                                 exc_info=True)
            channel['waveform_measurements'] = self.meas_list

    def get_trigger(self):
        logger.debug("getting trigger")
        trigger_dict = {
            'type': '',
            'coupling': '',
            'source': '',
            'level': '',
        }
        for name in trigger_dict:
            trigger_dict[name] = getattr(self.instr.trigger, name)
        self.ce_dict['trigger_edge_slope'] = self.instr.trigger.edge.slope
        return trigger_dict

    def get_acquisition(self):
        logger.debug("getting acquisition")
        for key in self.acq_dict:
            self.acq_dict[key] = getattr(self.instr.acquisition, key)
        return self.acq_dict

    def get_standard_waveform(self, index=0):
        logger.debug("getting standard_waveform")
        standard_waveform = self.instr.outputs[index].standard_waveform
        std_wave_dict = {
            'waveform': '',
            'frequency': '',
            'amplitude': '',
            'dc_offset': '',
            'duty_cycle_high': '',
            'start_phase': '',
            'pulse_width': '',
            'symmetry': '',
        }
        if standard_waveform:
            for key in std_wave_dict:
                std_wave_dict[key] = getattr(standard_waveform, key)
        else:
            logger.debug("no standard_waveform object")
            logger.debug("outputs[0] dir: %s" % dir(self.instr.outputs[0]))

    def get_outputs(self, index=0):
        logger.debug("getting outputs")
        outputs = None
        try:
            outputs = self.instr.outputs[index]
        except Exception:
            logger.debug("getting outputs exception")
        output_dict = {
            'impedance': '',
            'enabled': '',
        }
        if not outputs:
            return output_dict

        for key in output_dict:
            output_dict[key] = getattr(outputs, key)
            logger.debug("output from instr: %s %s" % (key, output_dict[key]))
        output_dict['standard_waveform'] = self.get_standard_waveform()
        self.ce_dict['outputs_noise_percent'] = outputs.noise.percent
        return output_dict

    def _get_excerpt_channel_data(self):
        """updates config exerpt to match instrument reported channel enabled,
           offset, range, and coupling. Updates enabled list to match
           instrument reported enabled channels. Returns copy of updated
           config excerpt"""
        logger.debug("updating config_excerpt, requesting channels")
        if not self.ivi_channels:
            self.ivi_channels = self.instr.channels
        config_excerpt = copy.deepcopy(self.ce_dict)
        self.enabled_list = []
        channels = []
        for channel in self.ce_dict['channels']:
            ch = channel['name']
            ch_dict = collections.defaultdict(str)
            logger.debug("requesting channel enabled data for %s" % ch)
            ch_idx = self.ch_idx_dict[ch]
            ch_dict['enabled'] = self.ivi_channels[ch_idx].enabled
            time.sleep(0.1)
            if ch_dict['enabled']:
                logger.debug("response %s enabled" % ch)
                ch_dict['name'] = self.ivi_channels[ch_idx].name
                ch_dict['offset'] = self.ivi_channels[ch_idx].offset
                time.sleep(0.1)
                ch_dict['range'] = self.ivi_channels[ch_idx].range
                time.sleep(0.1)
                if hasattr(self.ivi_channels[ch_idx], 'position'):
                    ch_dict['position'] = self.ivi_channels[ch_idx].position
                time.sleep(0.1)
                ch_dict['coupling'] = self.ivi_channels[ch_idx].coupling
                time.sleep(0.1)
                cii = self.ivi_channels[ch_idx].input_impedance
                time.sleep(0.1)
                ch_dict['input_impedance'] = cii
                if ch not in self.enabled_list:
                    self.enabled_list.append(ch)
            else:
                logger.debug("response: %s NOT enabled" % ch)
            self._update_channels(channels, ch_dict)
        config_excerpt['channels'] = channels
        # sync up excerpt list with transformer list
        self.ce_dict['enabled_list'] = self.enabled_list
        config_excerpt['enabled_list'] = self.enabled_list
        return config_excerpt

    def get_config_excerpt(self):
        logger.debug("getting config_excerpt")
        if cfg.getboolean('client', 'SIMULATED'):
            return DEFAULT_TEK_CONFIG
        config = self._get_base_config_excerpt()
        extras = self._get_config_excerpt_extras()
        if extras is not None and extras != {}:
            config.update(extras)
        return config

    def _get_base_config_excerpt(self):
        """Get config excerpt fields common to all scopes"""
        config_excerpt = self._get_excerpt_channel_data()
        config_excerpt['trigger'] = self.get_trigger()
        config_excerpt['acquisition'] = self.get_acquisition()
        return config_excerpt

    def _get_config_excerpt_extras(self):
        """Get fields beyond the base config excerpt"""
        extras = {}
        extras['outputs'] = self.get_outputs()
        extras['timebase'] = self.get_timebase()
        return extras

    def get_timebase(self):
        timebase = collections.defaultdict(int)
        try:
            timebase['position'] = self.instr.timebase.position
        except Exception:
            logger.debug("get timebase position exception")
        return timebase

    def get_probe_ids(self, total_channels=2):
        logger.debug("getting probe_ids")
        probe_ids = []
        if not self.ivi_channels:
            self.ivi_channels = self.instr.channels
        for i in range(total_channels):
            probe_ids.append(self.ivi_channels[i].probe_id)
        return probe_ids

    def get_voltage_list(self, waveform):
        logger.debug("getting voltage_list")
        voltage_list = [round_sig(float(point[1])) for point in waveform]
        return voltage_list

    def get_slice_list(self, voltage_list):
        """create list of slices sets class attribute"""
        logger.debug("getting slice_list")
        max_len = int(CLIENT_SETTINGS["MAX_LENGTH_FOR_BROWSER"])
        if len(voltage_list) >= max_len:
            slice_list = [voltage_list[x:x + max_len]
                          for x in range(0, len(voltage_list), max_len)]
        else:
            slice_list = [voltage_list]
        return slice_list

    def _grab_and_post_screenshot(self):
        if cfg.getboolean('client', 'SIMULATED'):
            return
        png = self.instr.display.fetch_screenshot()
        self.logger.info("_grab_and_post_screenshot")
        filename = "screenshot-" + self.metadata['result_id']
        pngfile = os.path.join(TMPDIR, 'tempfile.png')
        with open(pngfile, 'w') as f:
            f.write(png)
        response = self.gzip_and_post_file(pngfile, file_key=filename)
        self.screenshot_blob_key = response.text
        self.trace_dict['screenshot_blob_key'] = response.text

    def _quick_post_results(self):
        """Gives the quick feedback to the server for UI feedback

        Sends the first slice along with channel metadata needed
        to plot the data.

        Also calls _post_summary_waveform() for the overall data
        that is used to plot the summary waveform at the top of
        the waveform chart.
        """
        if self.capture_mode:
            config_name = str(self.command_id)
        else:
            config_name = self.config['name']
        self._set_divisions()
        if self.slice_dict:
            slice_list_len = len(self.slice_dict.itervalues().next())
        else:
            slice_list_len = 0
        first_y_values = self.first_slice.values()
        if len(first_y_values) == 0:
            slice_length = 0
        else:
            slice_length = len(first_y_values[0])
        slice_metadata = {
            'num_of_slices': slice_list_len,
            'slice_length': slice_length,
            'total_points': self.waveform_length,
        }
        self.metadata.update(slice_metadata)
        self.metadata['screenshot_blob_key'] = self.screenshot_blob_key
        # result_info['data'] = self.first_slice
        result = {
            'command_id': self.command['id'],
            'config_name': config_name,
            'instrument_type': self.command['info']['instrument_type'],
            'category': self.category,
            'tags': self.command['tags'],
            'device_under_test': self.device_under_test,
            'step_id': self.command['step_id'],
            'plan_id': self.command['plan_id'],
            'info': self.metadata,
        }
        r_url = BASE_URL + '/results'
        headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
        json_data = json.dumps({'result': result}, ensure_ascii=True)
        response = self.post(r_url, data=json_data, headers=headers)
        try:
            self.logger.info("_quick_post_results response.status_code: %s"
                             % response.status_code)
            result_id = json.loads(response.text)['result']['id']
        except Exception as e:
            logger.warning(e, exc_info=True)
            result_id = ''
        self.metadata['result_id'] = result_id
        url = BASE_URL + '/results/%s/slices/metadata' % result_id
        r = self.post(url, data=json.dumps({'num_of_slices': slice_list_len}))
        logger.info("slices/metadata post response %s" % r.text)
        self._post_summary_waveform()
        c_url = BASE_URL + '/commands'
        command_data = {
            'id': self.command['id'],
            'status': 'partial results',
            'results': [{'result_id': result_id}],
        }
        response = self.put(c_url, data=json.dumps(command_data))

    def _set_divisions(self, h_divs=0, v_divs=0):
        if self.instr._horizontal_divisions:
            self._horizontal_divisions = self.instr._horizontal_divisions
        else:
            self._horizontal_divisions = 10
        if self.instr._vertical_divisions:
            self._vertical_divisions = self.instr._vertical_divisions
        else:
            self._vertical_divisions = 8
        if h_divs:
            self._horizontal_divisions = h_divs
        if v_divs:
            self._vertical_divisions = v_divs
        self.trace_dict['h_divs'] = self._horizontal_divisions
        self.trace_dict['v_divs'] = self._vertical_divisions

    def get_horizontal_divisions(self):
        if self._horizontal_divisions:
            return self._horizontal_divisions
        else:
            self._set_divisions()
            return self._horizontal_divisions

    def get_vertical_divisions(self):
        if self._vertical_divisions:
            return self._vertical_divisions
        else:
            self._set_divisions()
            return self._vertical_divisions

    def post_status_update(self, status):
        status_url = ('https://' + COMMON_SETTINGS["DOMAIN"] + '/status/' +
                      COMMON_SETTINGS['COMPANYNAME'] + '/' +
                      COMMON_SETTINGS['HARDWARENAME'])
        self.post(status_url, status)

    def handle_usb_error(self, e):
        if e.args == ('Operation timed out',):
            logger.debug("Found USBError: Operation timed out")
            self.config_scorecard['errors']['usb_timeouts'] += 1
        elif e.args == ('Resource busy',):
            logger.debug('Found USBError: Resource busy')
            self.post_status_update(self.session, "Critical USBError")
            self.config_scorecard['errors']['usb_resource_busy'] += 1
        else:
            logger.debug('Unknown USBError')

    def update_scorecard_times(self):
        times = self.times
        stf = times['complete'] - times['init']
        lc = times['load_config_end'] - times['load_config_start']
        fm = times['fetch_measurements_end'] - \
            times['fetch_measurements_start']
        config_times = {
            'start_to_finish': stf,
            'load_config': lc,
            'fetch_measurements': fm,
        }
        self.config_scorecard['times'] = config_times

    def validate_config_excerpt(self, config):
        """Validates that the config

        Currently just checks that channels is in list format,
        converts dict format to list format, if it's neither
        then it just returns None.
        """
        validated_channels = []
        if 'channels' not in config:
            logger.warning("config is missing 'channels'")
            return None
        if isinstance(config['channels'], list):
            return self._validate_channels_list_config(config)
        if not isinstance(config['channels'], dict):
            logger.warning("unexpected type for config")
            return None
        for ch_key in config['channels']:
            valid_channel = {}
            channel = config['channels'][ch_key]
            for field in channel:
                clean_field = field.replace('channel_', '')
                valid_channel[clean_field] = channel[field]
            valid_channel['name'] = ch_key
            validated_channels.append(valid_channel)
        config['channels'] = validated_channels
        self._validate_channels_list_config(config)
        return config

    def _validate_channels_list_config(self, config):
        for idx, channel in enumerate(config['channels']):
            if idx > len(self._analog_channel_names):
                msg = "config has more channels than known analog channels"
                logger.error(msg)
                break
            if 'name' not in channel:
                est_ch = self._analog_channel_names[idx]  # use ivi given name
                msg = "Missing field 'name' from channel. Using %s" % est_ch
                logger.warning(msg)
                channel['name'] = est_ch
            if channel['name'] not in self._analog_channel_names:
                logger.warning("Channel %s is not an analog channel"
                               % channel['name'])
                channel['name'] = self._analog_channel_names[idx]
                logger.info("Assigning analog channel name %s"
                            % channel['name'])
            if 'enabled' not in channel:
                logger.info("Assuming %s enabled" % channel['name'])
                channel['enabled'] = True
        return config


class TransformerMSO5204B(ScopeTransformer):

    def __init__(self, setup, instrument, session):
        ScopeTransformer.__init__(self, setup, instrument, session)
        self.acq_dict = {
            'type': '',
            'start_time': '',
            'number_of_averages': '',
            'number_of_envelopes': '',
            'sample_rate': '',
            'time_per_record': '',
            'record_length': '',
        }
        if 'horizontal' in self.ce_dict:
            data = self.ce_dict['horizontal']
            self.horiz_dict = collections.defaultdict(int, data)
        else:
            logger.warning("MSO5204B missing 'horizontal' in config")
            self.horiz_dict = collections.defaultdict(int)

    def load_special_config_fields(self):
        self._set_timebase()

    def _set_acquisition(self, acq_dict):
        self._validate_acq_dict(acq_dict)
        try:
            if self.horiz_dict['sample_rate']:
                acq_dict['sample_rate'] = self._sample_rate_lookup(
                    self.horiz_dict['sample_rate'])
        except Exception:
            logger.debug(traceback.format_exc())

        for key in acq_dict:
            self.set_adders += 1

            # should these be removed from the input config on the server? TS
            if key == 'number_of_points_minimum':
                pass
            elif key == 'time_per_record':
                pass
            elif key == 'record_length':
                pass
            else:
                self._setinstr_with_tries(self.instr.acquisition, key,
                                          acq_dict[key], label='acquisition_',
                                          tries=3)

    def _get_config_excerpt_extras(self):
        extras = {}
        extras['timebase'] = self.get_timebase()
        return extras

    def get_timebase(self):
        timebase = collections.defaultdict(int)
        try:
            timebase['position'] = self.instr.timebase.position
        except Exception:
            logger.debug("get timebase position exception")
        try:
            timebase['scale'] = self.instr.timebase.scale
        except Exception:
            logger.debug("get timebase scaleexception")
        return timebase

    def _set_timebase(self):
        timebase_dict = collections.defaultdict(str)
        try:
            if self.horiz_dict['scale']:
                scale_string = self.horiz_dict['scale']
                timebase_dict['scale'] = self._scale_lookup(scale_string)
        except Exception:
            logger.debug(traceback.format_exc())
        for key in timebase_dict:
            self.set_adders += 1
            self._setinstr_with_tries(self.instr.timebase, key,
                                      timebase_dict[key], label='timebase_',
                                      tries=3)

    def _sample_rate_lookup(self, scale_string):
        sample_rate_table = {"400GS/s": 400e9,
                             "200GS/s": 200e9,
                             "80GS/s": 80e9,
                             "40GS/s": 40e9,
                             "20GS/s": 20e9,
                             "10GS/s": 10e9,
                             "5GS/s": 5e9,
                             "2.5GS/s": 2.5e9,
                             "1GS/s": 1e9,
                             "500MS/s": 500e6,
                             "200MS/s": 200e6,
                             "100MS/s": 100e6,
                             "50MS/s": 50e6,
                             "20MS/s": 20e6,
                             "10MS/s": 10e6,
                             "5MS/s": 5e6,
                             "2MS/s": 2e6,
                             "1MS/s": 1e6,
                             "500Ks/s": 500000,
                             "200Ks/s": 200000,
                             "100Ks/s": 100000,
                             "50Ks/s": 50000,
                             "20Ks/s": 20000,
                             "10Ks/s": 10000,
                             "5kS/s": 5000,
                             "2kS/s": 2000,
                             "1kS/s": 1000,
                             "500S/s": 500,
                             "200S/s": 200,
                             "100S/s": 100,
                             "50S/s": 50,
                             "20S/s": 20,
                             "10S/s": 10,
                             "5S/s": 5}
        sample_rate = str(sample_rate_table[scale_string])
        return sample_rate

    def _scale_lookup(self, value):
        value = value[0]
        scale_table = {"1ks": 1000,
                       "500s": 500,
                       "200s": 200,
                       "100s": 100,
                       "50s": 50,
                       "20s": 20,
                       "10s": 10,
                       "5s": 5,
                       "2s": 2,
                       "1s": 1,
                       "500ms": 0.5,
                       "200ms": 0.2,
                       "100ms": 0.1,
                       "50ms": 0.05,
                       "20ms": 0.02,
                       "10ms": 0.01,
                       "5ms": 0.005,
                       "2ms": 0.002,
                       "1ms": 0.001,
                       "500us": 5e-4,
                       "200us": 2e-4,
                       "100us": 1e-4,
                       "50us": 5e-5,
                       "20us": 2e-5,
                       "10us": 1e-5,
                       "5us": 5e-6,
                       "2us": 2e-6,
                       "1us":   1e-6,
                       "500ns": 5e-7,
                       "200ns": 2e-7,
                       "100ns": 1e-7,
                       "50ns":  5e-8,
                       "20ns":  2e-8,
                       "10ns":  1e-8,
                       "5ns":   5e-9,
                       "2.5ns": 2.5e-9,
                       "1ns":   1e-9,
                       "500ps": 5e-10,
                       "250ps": 2.5e-10}
        scale = scale_table[value]
        return scale


class TransformerMDO3012(ScopeTransformer):

    def __init__(self, setup, instrument, session):
        ScopeTransformer.__init__(self, setup, instrument, session)
        self._analog_channel_names = self.channel_names[:2]

    def _set_divisions(self, v_divs=8, h_divs=10):
        self._vertical_divisions = v_divs
        self._horizontal_divisions = h_divs


class RigolTransformer(ScopeTransformer):

    def __init__(self, setup, instrument, session):
        ScopeTransformer.__init__(self, setup, instrument, session)
        self._analog_channel_names = self.channel_names[:4]
        self.ch_idx_dict = {
            'chan1': 0,
            'chan2': 1,
            'chan3': 2,
            'chan4': 3,
        }
        self.acq_dict = {
            'time_per_record': '',
            'number_of_points_minimum': '',
            'type': '',
            'start_time': '',
            'number_of_averages': '',
            'record_length': '',
        }
        self.dec_factor = 1
        self.channel_settings = ['offset', 'range', 'coupling',
                                 'input_impedance']

    def get_outputs(self, index=0):
        pass

    def get_acquisition(self):
        logger.debug("getting acquisition")
        for key in self.acq_dict:
            if key == 'record_length':
                self.acq_dict[key] = self.waveform_length
            else:
                self.acq_dict[key] = getattr(self.instr.acquisition, key)
        return self.acq_dict

    def fetch_raw_setup(self, last_try=False):
        raw_setup = super(RigolTransformer, self).fetch_raw_setup()
        return raw_setup.encode('hex')

    def load_raw_setup(self, try_count=0):
        logger.debug("loading raw setup")
        hex_config = self.config['info']['raw_setup'].decode('hex')
        try:
            self.instr.system.load_setup(hex_config)
        except Exception:
            self.logger.warning("failed loading raw setup", exc_info=True)
            if try_count > 10:
                logger.debug("not retrying")
            else:
                self.instr.close()
                time.sleep(1)
                logger.debug("retrying...")
                try_count = try_count + 1
                self.instr = gateway_helpers.get_instrument(self.command)
                self.load_raw_setup(try_count)

    def _setinstr_with_tries(self, ivi_obj, key, value, label='', tries=3):
        success = False
        for attempt in range(tries):
            try:
                if key == 'number_of_points_minimum':
                    self.instr._write(":run")
                    time.sleep(1)
                    setattr(ivi_obj, key, value)
                    self.instr._write(":stop")
                else:
                    setattr(ivi_obj, key, value)
                success = True
                break
            except usb.core.USBError as e:
                logger.debug("USB Error in setting instrument", trace=True)
                self.handle_usb_error(e)
            except Exception:
                logger.debug("failed to set timebase: %s %s" %
                             (key, value), trace=True)
                self.exception_count += 1
                time.sleep(0.1)
        if success:
            self.config_scorecard['success'].append(label + key)
        else:
            self.config_scorecard['failure'].append(label + key)

    def _fetch_waveform(self, channel_name):
        self.instr._write(":WAVeform:MODE RAW")
        super(RigolTransformer, self)._fetch_waveform(channel_name)
        trigger_level = 0
        try:
            trigger_level = self.instr.trigger.level
            self.metadata['trigger_level'] = trigger_level
        except Exception:
            post_log("exception in getting trigger_level...%s"
                     % traceback.format_exc())
        for channel in self.channels:
            channel['trigger_level'] = trigger_level
        return self.metadata

    def check_instrument_ready(self):
        """Simply returns True since the Rigol has no busy? check"""
        return True


class TransformerMSO2302A(RigolTransformer):

    def __init__(self, setup, instrument, session):
        super(TransformerMSO2302A, self).__init__(setup, instrument, session)


class TransformerDS1054Z(RigolTransformer):

    def __init__(self, setup, instrument, session):
        super(TransformerDS1054Z, self).__init__(setup, instrument, session)
        # print self.meas_list
        # del self.meas_list[0:2]
        # del self.meas_list[-2]
        # rtime =  {
        #         'ivi_name': 'rtime',
        #         'display_name': 'Rise Time',
        #         'units': 's',
        #         }
        # ftime = {
        #         'ivi_name': 'ftime',
        #         'display_name': 'Fall Time',
        #         'units': 's',
        #          }

        # self.meas_list.insert(0, rtime)
        # self.meas_list.insert(1, ftime)

        # print 'meas_list', self.meas_list


class TransformerMSO2024(ScopeTransformer):

    """overrides get_config_excerpt to skip outputs"""

    def __init__(self, *args, **kwargs):
        super(TransformerMSO2024, self).__init__(*args, **kwargs)
        self._vertical_divisions = 8
        self._horizontal_divisions = 10

    def _get_config_excerpt_extras(self):
        return {}

    def check_instrument_ready(self):
        """Simply return True, MSO2024 has no ask('busy?')"""
        return True

    def _set_divisions(self, v_divs=8, h_divs=10):
        self._vertical_divisions = v_divs
        self._horizontal_divisions = h_divs

    def _alt_get_acquisition(self):
        """Alternative to convert acq to valid values

           Use this if ivi starts returning weird values for
           acquisition again
        """
        logger.debug("getting acquisition")
        for key in self.acq_dict:
            value = getattr(self.instr.acquisition, key)
            if key == 'time_per_record':
                value = self._convert_special_acq(value)
            self.acq_dict[key] = value
        return self.acq_dict

    def _convert_special_acq(self, value):
        if value < 100000:
            return value
        elif value < 500000:
            value = 100000
        elif value < 5000000:
            value = 1000000
        elif value < 50000000:
            value = 10000000
        else:
            return value


class TransformerDPO3014(ScopeTransformer):

    def __init__(self, *args, **kwargs):
        super(TransformerDPO3014, self).__init__(*args, **kwargs)


class TransformerDPO3034(ScopeTransformer):

    def __init__(self, *args, **kwargs):
        super(TransformerDPO3034, self).__init__(*args, **kwargs)

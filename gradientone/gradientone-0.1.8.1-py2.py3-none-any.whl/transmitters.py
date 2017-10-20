#!/usr/bin/python

"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

"""


import collections
import gzip
import json
import os

import requests
import traceback
import zlib
from configparser import ConfigParser
from datetime import datetime
from requests_toolbelt.multipart.encoder import MultipartEncoder

import gateway_helpers
from gateway_helpers import logger, get_headers
from base import BaseClient
from scope import ScopeClient

from gradientone.transformers import Transformer

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
MAX_VALID_MEAS_VAL = 1000000000  # until scaling for all units is decided
# MAX_VALID_MEAS_VAL = 1e36

if COMMON_SETTINGS["DOMAIN"].find("localhost") == 0 or COMMON_SETTINGS["DOMAIN"].find("127.0.0.1") == 0:  # noqa
    BASE_URL = "http://" + COMMON_SETTINGS["DOMAIN"]
else:
    BASE_URL = "https://" + COMMON_SETTINGS["DOMAIN"]

CONFIG_URL = (BASE_URL + "/testplansummary/" +
              COMMON_SETTINGS['COMPANYNAME'] + '/' +
              COMMON_SETTINGS['HARDWARENAME'])


class Transmitter(BaseClient):
    # Transmits trace data received from instrument up to the server

    def __init__(self, command_id="unknown_id"):
        self.session = requests.session()
        self.session.headers.update(gateway_helpers.get_headers())
        trace_dict = {
            "command_id": command_id,
        }
        self.trace_dict = collections.defaultdict(str, trace_dict)
        self.command_id = command_id
        self.results_dict = collections.defaultdict(str)
        self.dec_factor = 1
        self.upload_polling_metadata = True
        self.metadata = {}

    def format_csv(self):
        pass

    def post_result(self):
        if "data" in self.results_dict.keys():
            del self.results_dict["data"]

        payload = {
            # 'result' is for the datastore entity
            'result': {
                'id': self.results_dict['result_id'],
                'command_id': self.results_dict['command_id'],
                'config_name': self.results_dict['config_name'],
                'instrument_type': self.results_dict['instrument_type'],
                'tags': self.results_dict['tags'],
                'plan_id': self.results_dict['plan_id'],
                'info': self.results_dict,
            },
            'fields': [
                {
                    'name': 'config_name',
                    'value': self.results_dict['config_name'],
                    'type': 'text'
                },
                {
                        'name': 'hardware_name',
                        'value': self.results_dict['hardware_name'],
                        'type': 'text'
                },
                {
                        'name': 'instrument_type',
                        'value': self.results_dict['instrument_type'],
                        'type': 'text'
                },
                {
                        'name': 'command_id',
                        'value': self.results_dict['command_id'],
                        'type': 'text'
                },
                {
                        'name': 'start_datetime',
                        'value': str(datetime.now()),
                        'type': 'text'
                },
            ],
            'index_name': 'results'
        }
        url = BASE_URL + "/results"
        self.post(url, data=json.dumps(payload))

    def generate_results_dict(self):
        self.results_dict['config_name'] = "unknown"

    def post_wrapper(self, url, data="", headers={}):
        """
        This is a wrapper function to the sessions.post function to capture
        errors in the log.
        :param url: the url that the post is going to
        :param data: the data. Should be a string, if it is a dict it will be
        serialized to JSON
        :param headers: the headers. If empty, will be set to the default
        value in get_headers
        """
        if not headers:
            headers = gateway_helpers.get_headers()
        if isinstance(data, dict):
            data = json.dumps(data)
        response = self.post(url, data=data, headers=headers)
        assert response.status_code == 200
        logger.debug(url + " response.reason= %s" % response.reason)
        logger.debug(url + " response.status_code=%s" % response.status_code)
        return response

    def test_complete(self):
        """transmit test complete function sends a json object that is used
           to update DB on test status. Primarily metadata and indexing.
           No waveforms are sent here.
        """
        logger.info("Posting results")
        self.generate_results_dict()
        self.post_result()
        self.metadata = self._get_metadata(self.results_dict)
        self.transmit_result_blob()
        data = json.dumps(self.metadata)
        if self.results_dict['config_name'] == 'I2C':
            # trigger the appropriate analysis handler
            _response = self.get(BASE_URL + "/analysis",
                                 params={"command_id": self.command_id,
                                         "suite": "skywave"})
            expected_result = "[\"/markers?command_id=" + str(
                self.command_id) + "\", \"/results/" + str(
                self.metadata['result_id']) + "/metadata\"]"
            assert _response.status_code == 200
            assert _response.text == expected_result
        if self.upload_polling_metadata:
            polling_metadata_url = (BASE_URL + "/polling/results/metadata/" +
                                    str(self.command_id))
            self.post(polling_metadata_url, data=data)
        data = {'id': self.command_id, 'status': 'complete',
                'results': [{'result_id': self.metadata['result_id']}]}
        commands_url = BASE_URL + "/commands"
        response = self.put(commands_url, data=json.dumps(data),
                            headers=get_headers())
        assert response.status_code == 200

    def transmit_result_blob(self, infile=''):
        """Sends test results to the blobstore

        End to end waveforms are sent here.
        """
        if not infile:
            filename = 'full-trace-%s.json' % self.metadata['result_id']
            infile = os.path.join(TMPDIR, filename)
        logger.debug("transmitting blob")
        gzip_file = infile + '.gz'
        config_name = self.trace_dict['config_name']
        if not os.path.exists(infile):
            logger.warning("%s does not exist" % filename)
            return
        with open(infile) as f_in, gzip.open(gzip_file, 'wb') as f_out:
            f_out.writelines(f_in)
        data_type = 'application/x-gzip'

        if self.trace_dict["command_id"] == "unknown_id":
            raise ValueError("can't upload with unknown_id")
        blobfile = str(config_name) + ':' + str(self.trace_dict['command_id'])
        multipartblob = MultipartEncoder(
            fields={
                'file': (blobfile, open(gzip_file, 'rb'), data_type),
                'command_id': str(self.trace_dict['command_id']),
                'file_key': gzip_file.split('/')[-1],
            }
        )
        blob_url = self.get(BASE_URL + "/upload/geturl")
        response = self.post(
            blob_url.text,
            data=multipartblob,
            headers={
                'Content-Type': multipartblob.content_type
            })

    def transmit_trace(self):
        """results transmission for generic instruments"""
        self.session = requests.session()
        self.session.headers.update(gateway_helpers.get_headers())
        try:
            logger.info("transmitting trace")
            # complete transmission indexing blobstore data
            self.test_complete()
        except Exception:
            logger.error("Exception occurred during trace transmission")
            logger.error(traceback.format_exc())
            SENTRY_CLIENT.captureException()
        finally:
            tid = self.trace_dict['command_id']
            self.post_logfile(command_id=tid)

    def _get_metadata(self, results_dict={}, handles=[]):
        """Returns a metadata object from the args passed

        Since this is just a base class, it ignores the handles
        kwarg that is used for things like channels
        """
        metadata = {}
        metadata.update(results_dict)
        return metadata


class CANOpenTransmitter(Transmitter):
    """
    Transmits data for CANOpen devices
    """

    def __init__(self, data=None, measurements=None,
                 config={"arg": "unknown_config", "id": "unknown_id"}):

        Transmitter.__init__(self, config["id"])
        # the data is a list of dictionaries, where each key is a column
        # header, and the value with that key is the row value at that column,
        # i.e., [{'y': 0, 'x1': 9.9, 'x2': 3.2},
        #        {'y': 1, 'x1': 9.8, 'x2': 3.1},]
        self.data = data
        # the units is a dictionary with the unit names of each column in the
        # data, i.e., {'y': 's', 'x1': 'm', 'x2': 'km'}
        self.config = config
        self.measurements = measurements
        if "id" in config.keys():
            self.command_id = config["id"]

        # do not upload any metadata
        self.upload_polling_metadata = False
        self.transformer = Transformer(None)
        self.transformer.trace_dict = data
        self.transformer.command_id = self.command_id

    def generate_results_dict(self):
        if self.config is not None:
            self.results_dict["config_name"] = self.config["arg"]
        else:
            self.results_dict["config_name"] = "unknown"
        self.results_dict["hardware_name"] = COMMON_SETTINGS['HARDWARENAME']
        self.results_dict["company_nickname"] = COMMON_SETTINGS['COMPANYNAME']
        self.results_dict["instrument_type"] = "Motor"
        self.results_dict["command_id"] = self.command_id
        if self.measurements:
            self.results_dict["measurements"] = self.measurements

    def post_result(self):
        payload = {
            'result': {
                'id': self.results_dict['result_id'],
                'command_id': self.results_dict['command_id'],
                'config_name': self.results_dict['config_name'],
                'instrument_type': self.results_dict['instrument_type'],
                'tags': self.results_dict['tags'],
                'plan_id': self.results_dict['plan'],
                'info': self.results_dict,
            },
            "fields": [{
                "name": "config_name",
                "value": self.results_dict["config_name"],
                "type": "text"
            },
                {
                    "name": "hardware_name",
                    "value": self.results_dict["hardware_name"],
                    "type": "text"
                },
                {
                    "name": "instrument_type",
                    "value": self.results_dict["instrument_type"],
                    "type": "text"
                },
                {
                    "name": "command_id",
                    "value": self.results_dict["command_id"],
                    "type": "text"
                },
                {
                    "name": "parameters",
                    "value": ", ".join(self.config["info"]["config_excerpt"]["properties"]),  # noqa
                    "type": "text"
                },
                {
                    "name": "start_datetime",
                    "value": str(datetime.now()),
                    "type": "text"
                }
            ],
            "index_name": "results"
        }
        url = BASE_URL + "/results"
        response = self.post(url, data=json.dumps(payload))
        assert response.status_code == 200
        self.results_dict['result_id'] = json.loads(response.text)['result']['id']
        self.transformer.metadata['result_id'] = self.results_dict['result_id']
        self.transformer._write_trace_dict()


class ScopeTransmitter(Transmitter, ScopeClient):
    """transmits data to server for scope information"""

    def __init__(self, transformer=None, trace_data=None, session=None):
        Transmitter.__init__(self)
        self.command = collections.defaultdict(int)
        if transformer:
            self.command.update(transformer.command)
            self.command_id = self.command['id']
            self.command_id = self.command['id']
            self.time_step = transformer.time_step
            # the transformer ce_dict holds initial instructions
            self.ce_dict = transformer.ce_dict
            self.config_scorecard = transformer.config_scorecard
            self.g1_measurement_results = transformer.g1_measurement_results
            self.channels = transformer.channels
            self.first_slice = transformer.first_slice
        else:
            logger.warning("ScopeTransmitter missing transformer!")
            self.ce_dict = {}
            self.time_step = 1.0
        self.trace_dict = collections.defaultdict(int)
        if trace_data:
            self.trace_dict.update(trace_data)

        self.metadata = transformer.metadata

        # this is updated with the reported config_excerpt
        if "config_excerpt" in self.trace_dict.keys():
            self.ce_dict.update(self.trace_dict['config_excerpt'])
        self.config_scorecard = transformer.config_scorecard

        if cfg.getboolean('client', 'SIMULATED'):
            self.ce_dict['enabled_list'] = ['ch1']
        self.generate_results_dict()
        self.dec_factor = 1
        self.slices = []

    def generate_results_dict(self):
        results_page_link = BASE_URL + '/result/' + self.metadata['result_id']
        screenshot_url = (BASE_URL + '/download?file_key=screenshot-' +
                          self.metadata['result_id'])
        self.metadata['scope_screenshot_url'] = screenshot_url
        self.results_dict = {
            'results_link': results_page_link,
            'hardware_name': COMMON_SETTINGS['HARDWARENAME'],
            'company_nickname': COMMON_SETTINGS['COMPANYNAME'],
            'test_plan': self.trace_dict['test_plan'],
            'config_name': self.trace_dict['config_name'],
            'channels': self.channels,
            'raw_setup': self.trace_dict['raw_setup'],
            'config_input': self.ce_dict,
            'config_excerpt': self.trace_dict['config_excerpt'],
            'config_scorecard': self.config_scorecard,
            'g1_measurement': self.trace_dict['g1_measurement'],
            'g1_measurement_results': self.g1_measurement_results,
            # for the Result datastore object, we need the following
            'command_id': self.trace_dict['command_id'],
            'instrument_type': self.trace_dict['instrument_type'],
            'category': '',
            'tags': [],
            'plan_id': '',
            'dut_id': '',
            # 'info': {'foo': 'bar'},  # extra result metadata
        }
        self.results_dict.update(self.metadata)

    def transmit_file(self, filepath, content_type='application/x-gzip'):
        """transmits file to blobstore

        - assumes the file is already gzipped
        - deletes the local file after successfully transmitting
        """
        command_id = str(self.trace_dict['command_id'])
        if not filepath:
            filepath = filename = command_id + "-file.gz"
        else:
            filename = filepath.split('/')[-1]
        multipartblob = MultipartEncoder(
            fields={
                'file': (filename, open(filepath, 'rb'), content_type),
                'command_id': command_id,
                'file_key': filename,
            }
        )
        resp = self.get(BASE_URL + "/upload/geturl")
        headers = {'Content-Type': multipartblob.content_type}
        response = self.post(resp.text, data=multipartblob,
                             headers=headers)
        if response.status_code == 200:
            logger.info("File upload for %s succeeded!" % filename)
            os.remove(filepath)
        else:
            logger.info("File upload for %s failed" % filename)

    def update_command_status(self, status):
        c_url = BASE_URL + '/commands'
        data = json.dumps({
                'command_id': self.command_id,
                'status': status,
            })
        self.put(c_url, data)

    def transmit_slices(self):
        # post slices
        self.update_command_status('transmitting slices')
        slice_dir = os.path.join(gateway_helpers.DIRPATH, 'slices')
        if not os.path.exists(slice_dir):
            os.makedirs(slice_dir)
        voltage_start_time = 0
        dict_of_slice_lists = collections.defaultdict(int)
        list_of_slices = []
        for channel in self.trace_dict['channels']:
            voltages = channel['y_values']
            # create list of slices
            list_of_slices = [voltages[x:x + int(CLIENT_SETTINGS['MAX_LENGTH_FOR_BROWSER'])]  # nopep8
                              for x in range(0, len(voltages), int(CLIENT_SETTINGS['MAX_LENGTH_FOR_BROWSER']))]  # nopep8
            dict_of_slice_lists[channel['name']] = list_of_slices
            logger.debug("length of list of slices for %s: %s"
                         % (channel['name'], len(list_of_slices)))
            self.metadata['total_points'] = len(voltages)
        result_id = self.metadata['result_id']
        for idx, slice_points in enumerate(list_of_slices):
            slices_by_channel = {}
            for ch in dict_of_slice_lists:
                if idx + 1 > len(dict_of_slice_lists[ch]):
                    logger.debug("""Warning! Slice index greater than length of
                        list of slices for %s""" % ch)
                else:
                    slices_by_channel[ch] = dict_of_slice_lists[ch][idx]
            voltage_start_time += self.time_step * len(slice_points)
            slice_data = {
                'result_id': result_id,
                'command_id': self.trace_dict['command_id'],
                'slice_index': idx,
                'num_of_slices': len(list_of_slices),
                'voltage_start_time': voltage_start_time,
                'time_step': self.time_step,
                'data': slices_by_channel,
            }
            self.slices.append(slice_data)
            slice_data = zlib.compress(json.dumps(slice_data))
            filename = result_id + '-slice-' + str(idx) + '.json.gz'
            slice_file = os.path.join(slice_dir, filename)
            with open(slice_file, 'w') as f:
                f.write(slice_data)
        self.metadata['num_of_slices'] = len(list_of_slices)
        max_len = int(CLIENT_SETTINGS['MAX_LENGTH_FOR_BROWSER'])
        slice_length = max_len
        if 'total_points' in self.metadata:
            if self.metadata['total_points'] < max_len:
                slice_length = self.metadata['total_points']
        self.metadata['slice_length'] = slice_length
        self.transmit_slices_in_dir()

    def transmit_slices_in_dir(self, slice_dir=None):
        if not slice_dir:
            slice_dir = os.path.join(gateway_helpers.DIRPATH, 'slices')
        if not os.path.exists(slice_dir):
            return
        for filename in os.listdir(slice_dir):
            if '-slice-' in filename and filename.endswith(".gz"):
                slice_file = os.path.join(slice_dir, filename)
                self.transmit_file(slice_file)
                result_id = filename.split('-slice-')[0]
                slice_idx = filename.split('-slice-')[-1].split('.')[0]
                metadata = {
                    'result_id': result_id,
                    'slice_index': slice_idx,
                    'ready': True,
                }
                url = BASE_URL + '/results/' + result_id + '/slices/metadata'
                self.put(url, data=json.dumps(metadata))

    def transmit_config(self):
        """Posts config to server for storage"""
        if 'raw_setup' in self.trace_dict:
            info = {'raw_setup': self.trace_dict['raw_setup']}
        else:
            info = {}
        payload = {
            'config_excerpt': self.trace_dict['config_excerpt'],
            'config_data': {
                'new_config_name': self.trace_dict['command_id'],
                'info': info,
                'instrument_type': self.trace_dict['instrument_type'],
                'company_nickname': COMMON_SETTINGS['COMPANYNAME'],
            }
        }
        create_config_url = BASE_URL + "/create_config"
        _response = self.post(
            url=create_config_url,
            data=json.dumps(payload),
            headers=get_headers())
        assert _response.status_code == 200

    def transmit_logs(self, to_blob=False):
        filename = str(self.command_id) + '.log'
        if to_blob:
            # TODO: add functionality
            # transmit_logs(command_id=self.command_id)
            return
        # else it will just go to memcache
        multipartblob = MultipartEncoder(
            fields={
                'logfile': (filename, open('client.log', 'rb'), 'text/plain'),
                'testrunid': str(self.command_id),
            }
        )
        log_url = "https://" + \
            COMMON_SETTINGS['DOMAIN'] + "/logs/" + str(self.command_id)
        headers = {'Content-Type': multipartblob.content_type}
        resp = self.post(log_url, data=multipartblob, headers=headers)
        logger.debug(resp.text)

    def transmit_trace(self):
        """results transmission for scopes"""
        self.session = requests.session()
        self.session.headers.update(gateway_helpers.get_headers())
        try:
            logger.debug("transmitting trace")
            self.transmit_slices()

            # complete transmission indexing blobstore data
            self.test_complete()
        except Exception:
            logger.error("Exception occurred during trace transmission")
            logger.error(traceback.format_exc())
            SENTRY_CLIENT.captureException()
        finally:
            tid = self.trace_dict['command_id']
            self.post_logfile(command_id=tid)

    def shrink(self, voltage_list, time_step, mode="normal", limit=400):
        len_voltage_list = len(voltage_list)
        dec_factor = len_voltage_list / int(limit)
        if dec_factor == 0:
            dec_factor = 1
        new_time_step = dec_factor * float(time_step)
        shrunk_list = []
        index = 0
        while index < len_voltage_list:
            if mode == "normal":
                shrunk_list.append(voltage_list[index])
                index += dec_factor
            else:  # implement other modes here
                pass
        shrunk_data = {
            'y_values': shrunk_list,
            'time_step': new_time_step,
        }
        return shrunk_data

    def generate_thumbnail_data(self):
        try:
            filename = 'full-trace-%s.json' % self.metadata['result_id']
            infile = os.path.join(TMPDIR, filename)
            with open(infile, 'r') as f:
                trace_data = json.loads(f.read())
            channels = []
            for ch in trace_data['channels']:
                shrunk_channel = {'name': ch['name']}
                data = self.shrink(ch['y_values'], ch['time_step'])
                shrunk_channel.update(data)
                channels.append(shrunk_channel)
            return {'channels': channels}
        except Exception as e:
            logger.warning(e, exc_info=True)

    def post_result(self):
        thumbnail_data = self.generate_thumbnail_data()
        # alias to shorten line length
        cfg_ex = self.results_dict['config_excerpt']
        payload = {
            # 'result' is for the datastore entity
            'result': {
                'id': self.results_dict['result_id'],
                'command_id': self.results_dict['command_id'],
                'config_nam': self.results_dict['config_name'],
                'instrument_type': self.results_dict['instrument_type'],
                'tags': self.results_dict['tags'],
                'plan_id': self.results_dict['plan_id'],
                'info': self.results_dict,
            },

            'fields': [
                {
                    'name': 'config_name',
                    'value': self.results_dict['config_name'],
                    'type': 'text'
                },
                {
                    'name': 'hardware_name',
                    'value': self.results_dict['hardware_name'],
                    'type': 'text'
                },
                {
                    'name': 'instrument_type',
                    'value': self.results_dict['instrument_type'],
                    'type': 'text'
                },
                {
                    'name': 'command_id',
                    'value': self.results_dict['command_id'],
                    'type': 'text'
                },
                {
                    'name': 'start_datetime',
                    'value': str(datetime.now()),
                    'type': 'text'
                },
                {
                    'name': 'thumbnail_json',
                    'value': json.dumps(thumbnail_data),
                    'type': 'text'
                },
                {
                    'name': 'record_length',
                    'value': cfg_ex['acquisition']['record_length'],
                    'type': 'number'
                },
                {
                    'name': 'acquisition_type',
                    'value': cfg_ex['acquisition']['type'],
                    'type': 'text'
                },
                {
                    'name': 'trigger_source',
                    'value': cfg_ex['trigger']['source'],
                    'type': 'text'
                },
                {
                    'name': 'trigger_type',
                    'value': cfg_ex['trigger']['type'],
                    'type': 'text'
                },
                {
                    'name': 'trigger_level',
                    'value': cfg_ex['trigger']['level'],
                    'type': 'number'
                },
            ],
            'index_name': 'results'
        }
        channels = self.results_dict['channels']
        channel_num = 0
        for channel in channels:
            channel_num += 1
            if not channel['name']:
                channel['name'] = 'ch' + str(channel_num)
            field = {
                'name': channel['name'] + '_enabled',
                'value': channel['enabled'],
                'type': 'text',
            }
            payload['fields'].append(field)
        for channel in self.results_dict['channels']:
            self._add_channel_measurement_fields(payload, channel)
            if 'y_values' in channel:
                del channel['y_values']  # remove because it's too large
        self._validate_fields(payload['fields'])
        url = BASE_URL + "/results"
        self.post(url, data=json.dumps(payload))

    def _add_channel_measurement_fields(self, payload, channel):
        if 'waveform_measurements' not in channel:
            msg = "no waveform_measurements to add measurement fields to"
            logger.warning(msg)
            return
        for measurement in channel['waveform_measurements']:
            field = self._get_measurement_field(measurement, channel)
            if field:
                payload['fields'].append(field)

    def _get_measurement_field(self, measurement, channel):
        field = {}
        try:
            field['name'] = channel['name'] + '_' + measurement['ivi_name']
            field['value'] = measurement['value']
            if field['value'] == 'N/A':
                return field
            field['type'] = 'number'
        except Exception as e:
            logger.warning(e, exc_info=True)
        return field

    def _validate_fields(self, fields):
        used_field_names = []
        for field in fields:
            if field['name'] in used_field_names:
                logger.warning("%s already used" % field['name'])
                fields.remove(field)
            val = field['value']
            if isinstance(val, (int, float)) and val > MAX_VALID_MEAS_VAL:
                val = MAX_VALID_MEAS_VAL
        return fields


class GRLTransmitter(ScopeTransmitter):
    """transmits data to server for GRL tests"""

    def __init__(self, transformer, trace_data):
        ScopeTransmitter.__init__(transformer, trace_data)

    def transmit_slices(self):
        # post slices
        headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
        slice_url = (BASE_URL + '/results/' + self.metadata['result_id'] +
                     '/slices')
        voltage_start_time = 0
        dict_of_slice_lists = collections.defaultdict(int)
        ch = 'ch1'
        voltages = self.trace_dict['channels'][0]['y_values']
        # create list of slices
        list_of_slices = [voltages[x:x + int(CLIENT_SETTINGS['MAX_LENGTH_FOR_BROWSER'])]  # nopep8
                          for x in range(0, len(voltages), int(CLIENT_SETTINGS['MAX_LENGTH_FOR_BROWSER']))]  # nopep8
        dict_of_slice_lists[ch] = list_of_slices
        logger.debug("length of list of slices for %s: %s" %
                     (ch, len(list_of_slices)))
        for slice_index, slice_points in enumerate(list_of_slices):
            slices_by_channel = {}
            for ch in dict_of_slice_lists:
                if slice_index + 1 > len(dict_of_slice_lists[ch]):
                    logger.debug("""Warning! Slice index greater than length of
                        list of slices for %s""" % ch)
                else:
                    slices_by_channel[ch] = dict_of_slice_lists[
                        ch][slice_index]
            voltage_start_time += self.time_step * len(slice_points)
            slice_data = {
                'command_id': self.trace_dict['command_id'],
                'result_id': self.metadata['result_id'],
                'slice_index': slice_index,
                'num_of_slices': len(list_of_slices),
                'voltage_start_time': voltage_start_time,
                'time_step': self.time_step,
                'data': slices_by_channel,
            }
            slice_data = json.dumps(slice_data, ensure_ascii=True)
            if cfg.getboolean('client', 'USE_GZIP'):
                headers['content-encoding'] = 'gzip'
                slice_data = zlib.compress(json.dumps(slice_data))
            self.post(slice_url, data=slice_data, headers=headers)

    def transmit_result_blob(self, infile='grl-data.json'):
        super(GRLTransmitter, self).transmit_result_blob(infile)

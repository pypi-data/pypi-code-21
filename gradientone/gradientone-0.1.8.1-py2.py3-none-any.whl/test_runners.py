"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

"""

import collections
import multiprocessing as multi
import traceback
import time
from configparser import ConfigParser
from json import dumps, loads

from enum import Enum

import usb
import requests  # please do not use 'from requests import session'

from gradientone.device_drivers.can.CANcard import CanFrame
from gradientone.gateway_helpers import get_headers, post_config_form

try:
    from urllib.parse import urljoin
except:
    from urlparse import urljoin

import gateway_helpers
import tek_grl_configs
from transformers import (
    Transformer, ScopeTransformer, TransformerMSO2302A, TransformerMSO5204B,
    TransformerMSO2024, TransformerMDO3012,
    )
from misc_transformers import TransformerGRLTest

from gradientone.device_drivers.can.can_helpers import \
    lookup_trace_variable_unit_name
from gradientone.device_drivers.can.motor import Motor, PROPERTIES
from gradientone.schema_forms.ADP05518 import TRACE_VARIABLES
from transmitters import (
    CANOpenTransmitter, ScopeTransmitter, GRLTransmitter,
    )


cfg = ConfigParser()
cfg.read('/etc/gradient_one.cfg')
COMMON_SETTINGS = cfg['common']
CLIENT_SETTINGS = cfg['client']


SENTRY_CLIENT = gateway_helpers.get_sentry()

if COMMON_SETTINGS["DOMAIN"].find("localhost") == 0 or COMMON_SETTINGS["DOMAIN"].find("127.0.0.1") == 0:  # noqa
    BASE_URL = "http://" + COMMON_SETTINGS["DOMAIN"]
else:
    BASE_URL = "https://" + COMMON_SETTINGS["DOMAIN"]

CLIENT_ID = 'ORIGINAL'
SAMPLE_FILE = 'MDO30121M.txt'
CONFIG_URL = (BASE_URL, '/testplansummary/' +
              COMMON_SETTINGS['COMPANYNAME'] + '/' +
              COMMON_SETTINGS['HARDWARENAME'])
DEFAULT_TEK_TYPE = 'TektronixMDO3012'

# Careful! Setting BREATH_TIME any lower can cause issues.
# The 'instance hours' issue can happen by repeatedly
# making 100 requests per second and every second.
# HTTPS requests don't work that quickly anyway,
# so going lower than 0.25 is a waste of bandwidth
BREATH_TIME = 0.25
MAX_RETRIES = 5

CANBUS_URL = urljoin(BASE_URL, "motor/canbus")

logger = gateway_helpers.logger


class MotorState(Enum):
    IDLE = 0
    HOMING = 1
    MOVING = 2
    RESETTING = 3


def canframe_to_dict(frame):
    command_code = frame.data[0] if len(frame.data) > 0 else None
    address = [frame.id / 256, frame.id % 256]
    frame_data = [int(_byte) for _byte in frame.data[1:]]
    return {"address": address, "command_code": command_code,
            "frame_data": frame_data, "explanation": frame.explanation,
            "written": True}


def convert_numpy_points(data_points):
    # removes numpy datatypes from data
    for i in range(len(data_points)):
        for key in data_points[i].keys():
            # purely for typing reduction
            dp = data_points[i][key]
            data_points[i][key] = dp if type(dp) == str or type(
                dp) == bool else float(dp)
    return data_points


class TestRunner(object):
    """TestRunner runs the 'test' instructions form the server

       Note that a 'test' is not always an actual pass/fail test,
       the 'test' could be a configured scope waveform trace, or
       just a powermeter reading, or instructions for a motor, etc.

       run_command - this is the top level function that gets
                       when the client code creates a test_run
       single_run - most test runs will call this for a single run
       get_trace - when a trace is needed from the instrument,
                   this uses a Transformer for the instrument
                   to pass instructions and get the trace data,
                   then returns a Transmitter to send to server
    """

    def __init__(self, session):
        super(TestRunner, self).__init__()
        self._test_run = None
        self.setup = None  # setup is being deprecated for 'command'
        self.command = None
        self.session = session
        headers = gateway_helpers.get_headers()
        self.session.headers.update(headers)

        # Timer sets and clears the timeouts
        self.timer = gateway_helpers.Timer()
        # the connection to the copley card
        self.card = None
        self.logger = logger

    @property
    def test_run(self):
        self._test_run = collections.defaultdict(str)
        if self.setup:
            self._test_run.update(self.setup)
        return self._test_run

    def run_command(self, command):
        self.command = command
        self.setup = command  # setup is being deprecated for 'command'
        # update command status to 'in progress'
        data = {
            'status': 'in progress',
            'command_id': command['id']
            }
        logger.info("Updating %s to a %s status"
                    % (command['id'], data['status']))
        response = self.session.put(BASE_URL + '/commands', data=dumps(data))
        assert response.status_code == 200

        trace = None
        if self.command['label'] == 'GRL':
            self.run_grl_test()
        elif command['category'] in ['Capture', 'Config']:
            trace = self.get_trace()
        elif self.command['label'] == 'reset_usb_device':
            gateway_helpers.reset_device_with_tag(command['device_tag'])
        else:
            logger.warning("test_run with no control commands:" +
                           str(self.command["id"]))
        if trace:
            transmit_ps = multi.Process(target=trace.transmit_trace,
                                        name='nanny_process:' +
                                             COMMON_SETTINGS['DOMAIN'])
            transmit_ps.start()

    def run_grl_test(self):
        grl = tek_grl_configs.Grl_Test()
        grl.run_grl_test()

    def gen_data(self):
        test_run_id = self.setup["id"]
        if test_run_id == 0:
            raise ValueError("Test run id is zero! Setup is:" + str(
                self.setup))
        return {"test_run_id": test_run_id}

    def _get_instrument(self):
        self.timer.set_timeout(30)
        instr = None
        try:
            logger.debug("getting instrument")
            instr = gateway_helpers.get_instrument(self.command['info'])
        except usb.core.USBError:
            logger.debug("USBError!")
            # reset and retry
            gateway_helpers.reset_device_with_tag()
            time.sleep(1)
            instr = gateway_helpers.get_instrument(self.command['info'])
        except Exception:
            logger.warning("Failed to get instrument instance", exc_info=True)
            SENTRY_CLIENT.captureException()
        if not instr:
            logger.warning("No instrument available for trace")
            return None
        self.timer.clear_timeout()
        return instr

    def _get_transformer(self, instr=None):
        command = self.command
        ses = self.session
        i_transformer = None
        try:
            info = collections.defaultdict(str, command['info'])
            logger.info("Getting transformer for %s" % info['instrument_type'])
            if info['instrument_type'] == 'TektronixMSO2024':
                i_transformer = TransformerMSO2024(command, instr, ses)
            elif info['instrument_type'] == 'TektronixMDO3012':
                i_transformer = TransformerMDO3012(command, instr, ses)
            elif info['instrument_type'] == 'RigolMSO2302A':
                i_transformer = TransformerMSO2302A(command, instr, ses)
            elif info['instrument_type'] == 'TektronixMSO5204B':
                i_transformer = TransformerMSO5204B(command, instr, ses)
            elif info['instrument_type'] == 'GenericScope':
                i_transformer = ScopeTransformer(command, instr, ses)
            elif info['g1_measurement'] == 'grl_test':
                i_transformer = TransformerGRLTest(command, instr, ses)
            else:
                i_transformer = Transformer(command, instr, ses)
        except Exception:
            logger.debug("unable to build transformer... no trace")
            logger.debug("closing intrument without receiving trace")
            if instr:
                instr.close()
            logger.debug(traceback.format_exc())
            SENTRY_CLIENT.captureException()
        return i_transformer

    def _get_transmitter(self, i_transformer=None, trace_data=None, session=None):  # noqa
        if not session:
            session = requests.session()
        if not trace_data:
            return CANOpenTransmitter()
        try:
            if trace_data['test_run']['g1_measurement'] == 'grl_test':
                return GRLTransmitter(i_transformer, trace_data)
            else:
                return ScopeTransmitter(i_transformer, trace_data)
        except TypeError:
            return ScopeTransmitter(i_transformer, trace_data)
        except KeyError:
            return ScopeTransmitter(i_transformer, trace_data)
        except Exception:
            logger.debug("Unexpected exception in getting transmitter")
            return None

    def get_trace(self):
        """ Gets a trace from the instrument.

            This uses a Transformer for the instrument to pass
            instructions and get the trace data, then returns a
            trace object. The trace object is an instance of
            Transmitter that transmits the trace results and test
            run related data. By default it will retry once in case
            it fails on the first try.
        """
        logger.debug("get_trace() called")
        # obtain instrument for trace
        instr = self._get_instrument()
        if not instr:
            return
        # get transformer for instrument
        i_transformer = self._get_transformer(instr)
        if not i_transformer:
            logger.error("Unable to get i_transformer. Closing instrument")
            instr.close()
            return

        # get trace from instrument by running setup with transformer
        trace = None
        try:
            logger.info("Running trace setup")
            trace = self.process_transformer(i_transformer)
            logger.info("Process_transformer complete")
        except KeyError:
            logger.warning("KeyError in running setup", exc_info=True)
            SENTRY_CLIENT.captureException()
            # no retry on key errors
        except Exception:
            logger.error("Run config failed. Unexpected error", exc_info=True)
            SENTRY_CLIENT.captureException()
            # unexpected error, try again
            logger.info("Retrying to transformer processing", exc_info=True)
            trace = self.process_transformer(i_transformer)
        finally:
            logger.debug("Instrument processing complete, closing connection")
            instr.close()
            return trace

    def get_initial_excerpt(self, i_transformer):
        """Returns the intial config excerpt from instrument

        It's important to call this before fetching measurements.
          1) It initializes the instrument and syncs up transformer
          2) It gets an initial state, which is good for debugging

        i_transformer: object that reads back the appropriate
                       fields for the instrument type

        """
        self.timer.set_timeout(240)
        initial_excerpt = None
        try:
            initial_excerpt = i_transformer.get_config_excerpt()
            msg = "initial config setup from instrument: %s" % initial_excerpt
            logger.debug(msg)
        except usb.core.USBError as e:
            logger.debug("USBError!")
            i_transformer.handle_usb_error(e)
        except Exception:
            logger.debug("exception in config_excerpt initialization")
            SENTRY_CLIENT.captureException()
        self.timer.clear_timeout()
        return initial_excerpt

    def load_config(self, i_transformer, trace_dict):
        """loads config to instrument"""
        test_run = self.test_run
        success = False
        if test_run['category'] == 'Capture' or test_run['category'] == 'Autoset':  # noqa
            logger.debug("measuring without loading config")
            trace_dict['config_name'] = str(test_run['id'])
            success = i_transformer.check_any_channel_enabled()
        else:
            trace_dict['config_name'] = self.config['name']
            self.timer.set_timeout(60)
            try:
                success = i_transformer.load_config()
            except usb.core.USBError as e:
                logger.debug("USBError!")
                i_transformer.handle_usb_error(e)
            except Exception:
                logger.debug("Exception in calling load_config()")
                logger.debug(traceback.format_exc())
                SENTRY_CLIENT.captureException()
            self.timer.clear_timeout()
        return success

    def get_meas_dict(self, i_transformer):
        logger.debug("initiate measurement")
        meas_dict = collections.defaultdict(str)
        i_transformer.instr.measurement.initiate()
        self.timer.set_timeout(300)
        try:
            meas_dict = i_transformer.fetch_measurements()
        except usb.core.USBError as e:
            logger.debug("USBError Fetching measurments")
            i_transformer.handle_usb_error(e)
        except Exception:
            logger.debug("fetch_measurements exception")
            logger.debug(traceback.format_exc())
            SENTRY_CLIENT.captureException()
        self.timer.clear_timeout()
        return meas_dict

    def get_metadata(self, i_transformer):
        metadata = collections.defaultdict(str)
        metadata.update(i_transformer.trace_dict)
        self.timer.set_timeout(120)
        try:
            # instrument fetch_setup dump
            metadata['raw_setup'] = i_transformer.fetch_raw_setup()
            # read instrument using ivi fields
            metadata['config_excerpt'] = i_transformer.get_config_excerpt()
        except Exception:
            logger.warning("post-trace fetch config exception", exc_info=True)
            metadata['raw_setup'] = collections.defaultdict(str)
            metadata['config_excerpt'] = collections.defaultdict(str)
            SENTRY_CLIENT.captureException()
        self.timer.clear_timeout()
        i_transformer.times['complete'] = time.time()
        i_transformer.update_scorecard_times()
        return metadata

    def update_with_test_run_info(self, trace_dict, test_run):
        trace_dict['test_plan'] = test_run['test_plan']
        trace_dict['test_run_id'] = test_run['id']
        trace_dict['instrument_type'] = test_run['info']['instrument_type']
        trace_dict['g1_measurement'] = test_run['g1_measurement']
        return trace_dict

    def process_transformer(self, i_transformer):
        """Runs the setup on the instrument to get trace with measurments

        Called by get_trace(), this function processes transformer to
        collect instrument data, including measurements, config, and
        other metadata. These make up a trace_dict that is passed to
        the Transmitter constructor.

            i_transformer: Transfomer object being processed. This is used
                           to build a trace_dict to then use for the
                           Transmitter contructor.

        Returns a Transmitter object to transmit the trace
        """
        if not i_transformer:
            logger.error("No transformer to process!")
            return
        test_run = self.test_run
        test_run.update(i_transformer.test_run)
        trace_dict = collections.defaultdict(str)
        ses = i_transformer.session
        self.config = i_transformer.config
        logger.debug("config in setup is: %s" % self.config)
        # sets the ivi usb timeout
        i_transformer.instr._interface.timeout = 25000
        # check for special grl_test
        if test_run['g1_measurement'] == 'grl_test':
            trace_dict['config_name'] = self.config['name']
            i_transformer.start_test()
            trace_dict['meas_dict'] = collections.defaultdict(str)
        else:
            trace_dict['initial_excerpt'] = self.get_initial_excerpt(
                i_transformer)  # noqa
            success = self.load_config(i_transformer, trace_dict)
            if not success:
                msg = "Unable to load config! No measurement collected"
                logger.warning(msg)
                return
            trace_dict['meas_dict'] = self.get_meas_dict(i_transformer)
        # update with transformer dict
        trace_dict.update(i_transformer.trace_dict)
        # update with test_run info, with priority over transformer
        self.update_with_test_run_info(trace_dict, test_run)
        # update with the collected trace metadata
        trace_dict.update(self.get_metadata(i_transformer))
        # build transmitter to return and eventually transmit trace
        my_transmitter = self._get_transmitter(i_transformer, trace_dict, ses)
        # if cloud capture then transmit configuration for server db storage
        category = test_run['category']
        if category == 'Capture' or category == 'Autoset':
            my_transmitter.transmit_config()

        return my_transmitter


class MotorClient(object):

    def __init__(self):
        self.session = requests.session()
        self.setup = collections.defaultdict(str)
        self.last_setup = None
        # the connection to the copley card
        self.card = None
        self.card = Motor(CLIENT_SETTINGS["CANOPEN_ADDRESS"])
        self.card.open(baud=1000000)
        try:
            self.card.clear_pdos()
        except Exception as e:
            logger.warning("clear_pdos() e: %s" % e)
        self.busy = False
        post_config_form([{
                "manufacturer": "Copley",
                "product": "ADP05518",
                "fancy_name": "CopleyAccelNet-ADP-055-18"
            }])
        self.start_time = time.time()
        self.insert_index = 0

    def gen_data(self):
        test_run_id = self.setup["id"]
        if test_run_id == 0:
            raise ValueError("Test run id is zero! Setup is:" + str(
                self.setup))
        return {"test_run_id": test_run_id}

    def get_frame(self, frame_index=-1):
        _data = self.gen_data()
        if frame_index:
            _data["frame_index"] = frame_index
        response = self.session.get(CANBUS_URL, headers=get_headers(),
                                    params=_data)
        assert response.status_code == 200
        response = response.json()
        if response == "No data found for request":
            return None
        return response

    def post_frame(self, frame):
        _data = self.gen_data()
        _data["frames"] = [canframe_to_dict(frame)]
        response = self.session.post(CANBUS_URL, headers=get_headers(),
                                     data=dumps(_data))
        assert response.status_code == 200

    def update_commands(self, status="complete"):
        _data = {"command_id": self.setup["id"], "status": status}
        response = self.session.put(urljoin(BASE_URL, "/commands"),
                                    headers=get_headers(),
                                    data=dumps(_data))
        assert response.status_code == 200

    def update_frame(self, new_vals, index=-1):
        _data = self.gen_data()
        if isinstance(new_vals, list):
            _data["frames"] = []
            if len(new_vals) == 0:
                logger.warning("no frames to update!")
                return
            for frame in new_vals:
                _data["frames"].append(canframe_to_dict(frame))
        else:
            if not isinstance(new_vals, dict):
                new_vals = canframe_to_dict(new_vals)
            _data.update(new_vals)
        logger.info("update frame is: "+str(_data))

        if "method" not in _data.keys():
            if index == -1:
                _data["method"] = "update"
            else:
                _data["method"] = "insert"
                _data["frame_index"] = index

        _data["time"] = str(time.time()-self.start_time)
        response = self.session.put(CANBUS_URL, headers=get_headers(),
                                    data=dumps(_data))
        assert response.status_code == 200

    def update_status(self, status):
        _data = {"gateway_name": COMMON_SETTINGS["HARDWARENAME"],
                 "status": status}
        response = self.session.post(urljoin(BASE_URL, "motor/status"),
                                     headers=get_headers(), data=dumps(_data))
        assert response.status_code == 200

    def run(self):
        while True:
            time.sleep(1)
            try:
                # first, get the incoming command
                gateway = COMMON_SETTINGS['HARDWARENAME']
                _data = {"command_index": 0, "status": "pending",
                         "tag": "Motor", "gateway": gateway}
                response = self.session.get(urljoin(BASE_URL, "commands"),
                                            headers=get_headers(),
                                            params=_data)
                assert response.status_code == 200
                response = response.json()
                if not isinstance(response, dict):
                    logger.warning("Response: "+str(response) + " not a dict!")
                    continue
                if "error" in response.keys():
                    continue
                self.setup = response
                self.busy = True
                if self.setup["label"] == "trace":
                    self.run_motor_trace()
                if self.setup["label"] == "start_canbus":
                    self.run_canbus()
                if self.setup["label"] == "stop_canbus":
                    # stop canbus doesn't do anything
                    self.update_commands()
                self.busy = False
            except Exception:
                SENTRY_CLIENT.captureException()

    def run_canbus(self):
        self.start_time = time.time()
        self.card.frames_list = []
        # get all frames
        incoming_frame = self.get_frame(frame_index=None)
        for retry_numb in range(MAX_RETRIES):
            if incoming_frame:
                break
            else:
                time.sleep(BREATH_TIME)
                incoming_frame = self.get_frame(frame_index=None)
        if not incoming_frame:
            # no frames received
            self.update_status("No Frames Received")
            logger.error("No frames received after " + str(MAX_RETRIES) +
                         " attempts")
            self.update_commands(status="failed")
            return
        else:
            if "frames" in incoming_frame:
                frames_to_write = incoming_frame["frames"]
            else:
                frames_to_write = [incoming_frame]
        self.insert_index = 0

        self.update_status("CAN Bus In Progress")
        for current_frame in range(len(frames_to_write)):
            frame_to_write = frames_to_write[current_frame]
            if "expression" in frame_to_write.keys():
                if frame_to_write["expression"] == "DOWNLOAD":
                    # insert a spacer frame so that the analysis doesn't
                    # trigger the data download
                    self.update_frame({"expression": "END DOWNLOAD",
                                       "method": "insert",
                                       "frame_index": self.insert_index+1},
                                      index=self.insert_index+1)
                    self.card.property_getter("trace_data", use_sdo=True)
                    logger.info("frames generated: "+str(
                        len(self.card.frames_list)))
                    download_first_frame = self.card.frames_list[0]
                    del self.card.frames_list[0]
                    # overwrite the first frame
                    self.update_canbus_response(download_first_frame)
                    self.update_frame({"method": "delete",
                                       "frame_index": self.insert_index})
                elif frame_to_write["expression"] == "WAIT FOR TRACE":
                    self.card.wait_for_trace(software_trace=False)
                    wait_first_frame = self.card.frames_list[0]
                    del self.card.frames_list[0]
                    self.update_canbus_response(wait_first_frame)
            else:
                frame_to_write["frame_index"] = self.insert_index
                if "written" not in frame_to_write:
                    frame_to_write["written"] = False
                if frame_to_write["written"]:
                    continue
                address = ((frame_to_write["address"][0] << 8) +
                           frame_to_write["address"][1])
                if "command_code" in frame_to_write.keys():
                    data = [frame_to_write["command_code"]]
                else:
                    data = []
                if "frame_data" in frame_to_write.keys():
                    data += frame_to_write["frame_data"]
                self.card.frames_list = []
                xmit_frame = CanFrame(id=address, data=data)
                self.card.send_ack(xmit_frame)
                self.update_canbus_response(frame_to_write)
        self.update_commands()
        logger.info("CanBus Done")
        self.update_status("Complete")

    def run_motor_trace(self):
        # Trace data mode
        state = MotorState.IDLE
        config_parts = ["motor_end_position", "properties", "time_window",
                        "trace"]

        logger.info("Started Motor Trace")

        self.update_status("Trace In Progress")
        self.card.clear_pdos()
        logger.info("Cleared PDOs")
        while True:
            if self.card.unplugged:
                return
            logger.info("Motor state is: "+str(state) + " setup is: " +
                        str(self.setup["id"]))

            if isinstance(self.setup["info"]["config_excerpt"], basestring):
                self.setup["info"]["config_excerpt"] = loads(self.setup["info"]["config_excerpt"])
            elif not isinstance(self.setup["info"]["config_excerpt"], dict):
                logger.error("config excerpt is unknown type: "+str(self.setup["info"]["config_excerpt"]))
            test_order = self.setup["info"]["config_excerpt"]
            #if isinstance(test_order, basestring):
            #    test_order = loads(test_order)
            if "node_id" in test_order.keys():
                self.card.node = test_order["node_id"]
            if "homing_tolerance" in test_order.keys():
                homing_tolerance = test_order["homing_tolerance"]
            else:
                homing_tolerance = 100
            if "monitor_registers" in test_order.keys():
                self.card.monitor_registers = test_order["monitor_registers"]
            else:
                self.card.monitor_registers = []

            if not isinstance(test_order, dict):
                raise ValueError("Config Excerpt is invalid "+test_order)
            if "time_window" not in test_order.keys():
                logger.warning("No time window, setting to 1")
                test_order["time_window"] = 1.0
            if "motor_end_position" not in test_order.keys():
                logger.warning("No Motor end position, setting to 0")
                test_order["motor_end_position"] = 0.0
            if state == MotorState.IDLE and \
                    not set(config_parts).issubset(test_order.keys()):
                msg = "In run motor, test order missing parts:" + str(
                    list(set(config_parts) - set(test_order.keys())))
                logger.error(msg)
                raise ValueError(msg)
            elif state == MotorState.IDLE:
                test_order["properties"] = [str(prop) for prop in
                                            test_order["properties"]]
                # set up parameters once
                if test_order["trace"] == "poll":
                    for parameter in test_order["properties"]:
                        self.card.property_getter(parameter)
                self.card.start_time = time.time()
                state = MotorState.HOMING
                if "homing_step" in test_order.keys():
                    if not test_order["homing_step"]:
                        state = MotorState.MOVING
            elif state == MotorState.HOMING:
                self.update_status("Homing Motor")
                self.card.move(0)
                if abs(self.card.property_getter("actual_position")) < homing_tolerance:
                    state = MotorState.MOVING
            if state == MotorState.MOVING:
                data_points = self.card.do_trace(destination=test_order["motor_end_position"],  # noqa
                                                 max_counts=-1,
                                                 max_time=test_order[
                                                     "time_window"],
                                                 properties=test_order[
                                                     "properties"],
                                                 poll=test_order[
                                                          "trace"] == "poll")
                # update the test to complete, then return to idle
                _data = self.gen_data()
                data_points = convert_numpy_points(data_points)
                _data["data"] = data_points
                _data["units"] = {}
                _data['config_name'] = self.setup['arg']
                for key in data_points[0].keys():
                    if key in PROPERTIES.keys():
                        _data["units"][key] = PROPERTIES[key]["units"]
                    elif key in TRACE_VARIABLES:
                        _data["units"][key] = lookup_trace_variable_unit_name(
                            key)

                if len(self.card.flag_timestamps) > 0:
                    measurements = {"flag_timestamps": self.card.flag_timestamps}
                else:
                    if self.card.monitor_registers:
                        logger.warning("The monitor registers were set to: "+str(self.card.monitor_registers)+" but no flags were detected!")
                    measurements = None
                transmitter = CANOpenTransmitter(
                    data=_data["data"],
                    units=_data["units"],
                    config=self.setup,
                    measurements=measurements
                    )
                transmitter.transmit_trace()
                logger.info("Done motor trace")
                state = MotorState.RESETTING
                if "homing_step" in test_order.keys():
                    if not test_order["homing_step"]:
                        self.update_status("Complete")
                        return
            elif state == MotorState.RESETTING:
                self.update_status("Resetting Motor")
                self.card.move(0)
                if abs(self.card.property_getter("actual_position")) < homing_tolerance:
                    self.update_status("Complete")
                    return

    def update_canbus_response(self, frame_to_write):
        # overwrite the first frame
        if frame_to_write is not None:
            if not isinstance(frame_to_write, dict):
                frame_to_write = canframe_to_dict(frame_to_write)
            if "frame_index" not in frame_to_write.keys():
                frame_to_write["frame_index"] = self.insert_index
            frame_to_write["written"] = True
            self.update_frame(frame_to_write)
            self.insert_index += 1
        if len(self.card.frames_list) > 0:
            self.update_frame(self.card.frames_list, index=self.insert_index)
            self.insert_index += len(self.card.frames_list)

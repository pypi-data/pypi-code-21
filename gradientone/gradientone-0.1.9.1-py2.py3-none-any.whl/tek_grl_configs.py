#!/usr/bin/env python

"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

"""

import gzip
import time
import traceback
import requests
import gateway_helpers
from requests_toolbelt.multipart.encoder import MultipartEncoder
from device_drivers import usb_controller
from gateway_helpers import logger


WAVE_FILEPATH = 'C:\GRL\GRL-USB_PD\SignalFiles\BIST_CM2_CCLine.wfm'
BASE_RUN = {
    'instrument_type': 'GenericTektronix',
    'instrument_ip_address': None,
    'usb_device_id': None,
    'usb_manufacturer_id': None,
}


class Grl_Test(object):
    def __init__(self):
        super(Grl_Test, self).__init__()
        self.exception_counter = 0
        try:
            logger.info("getting instrument")
            self.tek = gateway_helpers.get_instrument(BASE_RUN)
        except Exception:
            self.exception_counter += 1
            logger.info("exception getting instrument", exc_info=True)
        try:
            logger.info("getting instrument")
            self.usbc = usb_controller.RawUsbController(vendor_id=0x227f,
                                                        product_id=0x0002)
        except Exception:
            self.exception_counter = 0
            logger.info("exception getting usb controller", exc_info=True)

    def set(self, obj, attr, val):
        """Sets the objects attribute (attr) with the value supplied and logs
        the success or error"""
        try:
            setattr(obj, attr, val)
            logger.info("TEK SUCCESS set %s with %s" % (attr, val))
        except Exception:
            logger.info("TEK ERROR: %s not set with %s" % (attr, val))
            logger.debug(traceback.format_exc())
            self.exception_counter += 1

    def write(self, command="", tek=None):
        """Writes to the tek with the _write function and logs the success or
        error. If no tek is supplied, the class tek object will be used."""
        if not tek:
            tek = self.tek
        try:
            tek._write(command)
            logger.info("TEK SUCCESS write:%s" % command)
        except Exception:
            logger.info("TEK ERROR: exception with write:%s" % command)
            logger.debug(traceback.format_exc())
            self.exception_counter += 1

    def first_tek_commands(self, tek=None):
        commands = ["SELECT:CH1 ON", 
                    "SELECT:CH2 ON", 
                    "HORIZONTAL:ROLL AUTO",
                    "TRIGGER:A:MODE AUTO",
                    "ACQUIRE:STOPAFTER RUNSTOP",
                    "ACQUIRE:STATE 1",
                    "AUTOSet EXECute",
                    ":HORIZONTAL:Mode MANUAL",]
                    # May need to fix the REF1 path for the NUC filesystem
        for com in commands:
            self.write(command=com, tek=tek)
        time.sleep(6)
        commands = ["HORizontal:MODE:SCAle 0.1",
                    "HORizontal:MODE MANUAL",
                    "ACQuire:MODE HiRes",
                    "HORizontal:MODE:SAMPLERate 4000000",
                    "CH3:PROBECOntrol MANual",
                    "CH3:PROBE:FORCEDRANGE 30"]
        for com in commands:
            self.write(command=com, tek=tek)
        if not tek:
            tek = self.tek
        for ch in tek.channels[0:4]:
            self.set(ch, 'enabled', True)
        self.set(tek.timebase, 'scale', 0.2)
        acq_dict = { 
            'horizontal_mode': 'manual',
            'type': 'high_resolution',
            'sample_rate': '4000000',
            'number_of_points_minimum': '8000000',
        }
        for k,v in acq_dict.iteritems():
            self.set(tek.acquisition, k, v)
        self.set(tek.timebase, 'position', 10)
        for ch in tek.channels[0:1]:
            self.set(ch, 'offset', 0.9)
            self.set(ch, 'range', 3)
        for ch in tek.channels[1:2]:
            self.set(ch, 'offset', 7.4)
            self.set(ch, 'range', 20)
        for ch in tek.channels[2:3]:
            self.set(ch, 'offset', 0)
            self.set(ch, 'range', 10)
        self.set(tek.acquisition, 'type', 'high_resolution')
        self.set(tek.acquisition, 'horizontal_roll', 'off')
        trigger_dict = {
            'modifier': 'none',
            'type': 'edge',
            'source': tek.channels[1],
        }
        for k,v in trigger_dict.iteritems():
            self.set(tek.trigger, k, v)
        self.set(tek.trigger.edge, 'slope', 'positive')
        self.set(tek.trigger, 'level', 2.5)

    def first_pd_commands(self, usbc=None):
        if not usbc:
            usbc = self.usbc
        commands = ['\x14\x05', '\x1B\x03', '\x1C\x02', '\x1A\x02']
        for com in commands:
            usbc.write(command=com)

    def second_tek_commands(self, tek=None):
        if not tek:
            tek = self.tek
        for ch in tek.channels[0:1]:
            ch.offset = 0.956
            ch.range = 1.6
        tek.timebase.scale = 0.02
        tek.acquisition.horizontal_mode = 'manual'
        tek.acquisition.type = 'high_resolution' 
        # not sure if we are sending down 'high_resolution' or 'hires'
        tek.acquisition.number_of_points_minimum = 10000000 
        tek.acquisition.sample_rate = 50000000
        tek.timebase.position = 10
        for ch in tek.channels[1:2]:
            ch.offset = 11.1
            ch.range = 30

    def second_pd_commands(self, usbc):
        if not usbc:
            usbc = self.usbc
        # Payload =  0x3D 0x0 0x0 0x0 0x90 or 0x10 from scope wireshark 
        usbc.write(command='\x3D\x00\x00\x00\x10')

    def third_tek_commands(self, tek=None):
        if not tek:
            tek = self.tek
        self.set(tek.acquisition, 'horizontal_roll', 'off')
        trigger_dict = {
            'modifier': 'none',
            'type': 'edge',
            'source': tek.channels[3],
        }
        for k,v in trigger_dict.iteritems():
            self.set(tek.trigger, k, v)
        self.set(tek.trigger.edge, 'slope', 'either')
        self.set(tek.trigger, 'level', 0.6)
        for ch in tek.channels[3:4]:
            self.set(ch, 'offset', 0)
            self.set(ch, 'range', 25)
        tek.display.clear()
        tek.measurement.initiate()

    def third_pd_commands(self, usbc=None):
        # Payload =  0x1 0x43 0x10 0x0 0x0 0x0 0x50
        if not usbc:
            usbc = self.usbc 
        usbc.write(command='\xF2\x07\x01\x43\x10\x00\x00\x00\x50')

    def fourth_tek_commands(self, tek=None):
        if not tek:
            tek = self.tek
        tek._interface.timeout = 300
        # tek._ask('*OPC?')
        commands = ["SAVe:WAVEform:FILEFormat Internal", "DATa:STARt 0", 
                    "DATa:STOP 1E10", "SAVe:WAVEform CH1, REF1"]
                    # May need to fix the REF1 path for the NUC filesystem
        for com in commands:
            self.write(command=com, tek=tek)
        waveform = tek.channels[0].measurement.fetch_waveform()
        filename = "waveform.json.gz"
        with gzip.GzipFile(filename, 'w') as outfile:
            for data in waveform:
                outfile.write(json.dumps(data) + '\n')
        self.post_waveform_file(filename)
        logger.info("length of fetched waveform: %s" % len(waveform))
        # tek._ask('*OPC?') 
        self.set(tek.trigger, 'continuous', True)
        self.set(tek.acquisition, 'horizontal_roll', 'Auto')
        self.set(tek.trigger, 'modifier', 'auto')
        time.sleep(10)

    def fourth_pd_commands(self, usbc=None):
        if not usbc:
            usbc = self.usbc
        # Payload =  0x18 0x4
        usbc.write(command='\x18\x04')

    def fifth_tek_commands(self, tek=None):
        if not tek:
            tek = self.tek
        self.set(tek.acquisition, 'horizontal_roll', 'Auto')
        self.set(tek.trigger, 'modifier', 'auto')
        self.set(tek.trigger, 'continuous', True)

    def run_grl_test(self):
        self.exception_counter = 0
        code_blocks = [
            self.first_tek_commands,
            self.first_pd_commands,
            self.second_tek_commands,
            self.second_pd_commands,
            self.third_tek_commands,
            self.third_pd_commands,
            self.fourth_tek_commands,
            # fourth_pd_commands(self.usbc),
            # fifth_tek_commands(self.tek),
        ]
        # set sleep seconds for between blocks
        sleep_secs = 5

        for index, code_block in enumerate(code_blocks):
            try:
                code_block()
                logger.info("Ran code_blocks[%s], now sleeping %s sec(s)" 
                                 % (index, sleep_secs))
                time.sleep(sleep_secs)
            except Exception:
                logger.info("exception with code_blocks[%s]" % index)
                logger.info(traceback.format_exc())
                self.exception_counter += 1

        self.tek.close()
        return "test ran with %s exceptions" % self.exception_counter

    def post_waveform_file(self, filename):
        multipartblob = MultipartEncoder(
            fields = {
                'field0': (filename, open(filename, 'rb'), 'text/plain'),
                'company': COMPANYNAME,
            }
        )
        blob_url = requests.get("https://"
                   + DOMAIN + "/upload/grlfile/geturl")
        response = requests.post(blob_url.text, data=multipartblob,
                          headers={'Content-Type': multipartblob.content_type})
        logger.info("POST file response.reason: %s" % response.reason)
        logger.info("POST file response.status_code: %s" % response.status_code)
        self.waveform_blob_key = response.text

# Old Functions - Kept for reference
# first need to instantiate tek!
# for example:
# tek = gateway_helpers.get_instrument(BASE_RUN)

#scope commands

# def first_tek_commands(tek):
#     for ch in tek.channels[0:4]:
#         ch.enabled = True
#     tek.timebase_scale = 0.2
#     tek.acquisition.horizontal_mode = 'manual'
#     tek.acquisition.type = 'high_resolution' #not sure if we are sending down 'high_resolution' or 'hires'
#     tek.acquisition.sample_rate = 4000000
#     tek.acquisition.number_of_points_minimum = 8000000 
#     tek.timebase.position = 10
#     for ch in tek.channels[0:1]:
#         ch.offset = 0.9 
#         ch.range = 3
#     for ch in tek.channels[1:2]:
#         ch.offset = 7.4
#         ch.range = 20
#     for ch in tek.channels[2:3]:
#         ch.offset = 0 
#         ch.range = 10
#     tek.acquisition.type = 'high_resolution' #not sure if we are sending down 'high_resolution' or 'hires'
#     tek.acquisition.horizontal_roll = 'off'
#     tek.trigger.modifier = 'none'
#     tek.trigger.type = 'edge'
#     tek.trigger.source = tek.channels[1]
#     tek.trigger.edge.slope = 'positive'
#     tek.trigger.level = 2.5


# def first_pd_commands(usbc):
#     #send USB commands to the PD controller:
#     # Payload =  0x14 0x5 
#     # Payload =  0x1B 0x3 
#     # Payload =  0x1C 0x2 
#     # Payload =  0x1A 0x2 
#     usbc.write(command='\x14\x05')
#     usbc.write(command='\x1B\x03')
#     usbc.write(command='\x1C\x02')
#     usbc.write(command='\x1A\x02')


# def second_tek_commands(tek):
#     #scope commands
#     for ch in tek.channels[0:1]:
#         ch.offset = 0.956
#         ch.range = 1.6
#     tek.timebase_scale = 0.02
#     tek.acquisition.horizontal_mode = 'manual'
#     tek.acquisition.type = 'high_resolution' #not sure if we are sending down 'high_resolution' or 'hires'
#     tek.acquisition.number_of_points_minimum = 10000000 
#     tek.acquisition.sample_rate = 50000000
#     tek.timebase.position = 10
#     for ch in tek.channels[1:2]:
#         ch.offset = 11.1
#         ch.range = 30


# def second_pd_commands(usbc):
#     #send USB commands to the PD controller:
#     # Payload =  0x3D 0x0 0x0 0x0 0x90 
#     usbc.write(command='\x3D\x00\x00\x00\x90')


# def third_tek_commands(tek):
#     #scope commands
#     tek.acquisition.horizontal_roll = 'off'
#     tek.trigger.modifier = 'none'
#     tek.trigger.type = 'edge'
#     tek.trigger.source = tek.channels[3]
#     tek.trigger.edge.slope = 'either'
#     tek.trigger.level = 0.6
#     for ch in tek.channels[3:4]:
#         ch.offset = 0 
#         ch.range = 25
#     tek.display.clear()
#     tek.measurement.initiate()


# def third_pd_commands(usbc):
#     #send USB commands to the PD controller:
#     # Payload =  0x1 0x43 0x10 0x0 0x0 0x0 0x50 
#     usbc.write(command='\xF2\x07\x01\x43\x10\x00\x50')


# def fourth_tek_commands(tek):
#     #scope commands
#     # tek._ask('*OPC?')

#     #let's keep their file for comparison purposes
#     tek._write("SAVe:WAVEform:FILEFormat Internal")
#     tek._write("DATa:STARt 0")
#     tek._write("DATa:STOP 1E10")
#     tek._write("SAVe:WAVEform CH1, REF1")#Need to fix the path for the NUC filesystem
#     waveform = tek.channels[0].measurement.fetch_waveform()
#     with open("grl_waveform.txt", "w") as text_file:
#         text_file.write(str(waveform))
#     # tek._ask('*OPC?') 
#     tek.trigger.continuous = True
#     tek.acquisition.horizontal_roll = 'Auto'
#     tek.trigger.modifier = 'auto'


# def fourth_pd_commands(usbc):
#     #send USB commands to the PD controller:
#     # Payload =  0x18 0x4
#     usbc.write(command='\x18\x04')


# def fifth_tek_commands(tek):
#     #scope commands
#     tek.acquisition.horizontal_roll = 'Auto'
#     tek.trigger.modifier = 'auto'
#     tek.trigger.continuous = True


    # def run_grl_test(self):
        # try:
        #     first_tek_commands(self.tek)
        # except Exception:
        #     self.exception_counter += 1
        #     logger.info("exception with first tek commands")
        #     logger.info(traceback.format_exc())

        # try:
        #     first_pd_commands(self.usbc)
        # except Exception:
        #     self.exception_counter += 1
        #     logger.info("exception with first pd commands")
        #     logger.info(traceback.format_exc())

        # try:
        #     second_tek_commands(self.tek)
        # except Exception:
        #     self.exception_counter += 1
        #     logger.info("exception with second tek commands")
        #     logger.info(traceback.format_exc())

        # # try:
        # #     second_pd_commands()
        # # except Exception:
        # #     self.exception_counter += 1
        # #     logger.info("exception with second pd commands"

        # try:
        #     third_tek_commands(self.tek)
        # except Exception:
        #     self.exception_counter += 1
        #     logger.info("exception with third tek commands")
        #     logger.info(traceback.format_exc())

        # try:
        #     third_pd_commands(self.usbc)
        # except Exception:
        #     self.exception_counter += 1
        #     logger.info("exception with third pd commands")
        #     logger.info(traceback.format_exc())

        # try:
        #     fourth_tek_commands(self.tek)
        # except Exception:
        #     self.exception_counter += 1
        #     logger.info("exception with fourth tek commands")
        #     logger.info(traceback.format_exc())

        # # try:
        # #     fourth_pd_commands(self.usbc)
        # # except Exception:
        # #     self.exception_counter += 1
        # #     logger.info("exception with fourth pd commands"
        # #     logger.info(traceback.format_exc()

        # # try:
        # #     fifth_tek_commands(self.tek)
        # # except Exception:
        # #     self.exception_counter += 1
        # #     logger.info("exception with fourth pd commands"
        # #     logger.info(traceback.format_exc()

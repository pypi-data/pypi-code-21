#   --------------------------------------------------------------------------
#   Copyright 2011 SRE-F, ESA (European Space Agency)
#       Hans Smit <Hans.Smit@esa.int>
#   --------------------------------------------------------------------------
"""
This module reads out the XCAM data in buffered mode. Having this module
invoked externally ensures that the calling application does not "freeze"
while the readout takes place.

XCam QuickUSB command protocol::
    0x01, [2^(idx-1)], [val:lsb], [val:msb] // clock voltage
    0x02, [2^(idx-1)], [val:lsb], [val:msb] // bias voltage
    0x03, [val]                             // CCD power 0 (off) or 1 (on)
    0x04, [dex bytes]                       // set PA memory
    0x05, [dex bytes]                       // set DA memory
    0x06, [hex2], [hex0], [hex2]            // set PA memory location
    0x0b, [idx], [val:lsb], [val:msb]       // set DSP parameter
    0x0c, [val]                             // set gain command

    0x12                                    // eepver (read 12 bytes after)
    0x14                                    // cancel grab if read failed

    0x07,0x0F                               // reset fifo buffer
    0xFE,0xFF                               // normal cmd byte

"""
import sys
import os
import logging
import re
import time
import threading
import shutil
import platform
import ctypes
import random

import numpy

try:
    import QuickUsb
except OSError as impErr:
    print("QuickUsb failed to load:", impErr)


class XCamConst(object):

    XCAM_DIR = os.path.dirname(os.path.abspath(__file__))
    READOUT_EXE = '%s %s --readout {:d}' % (sys.executable, os.path.join(XCAM_DIR, 'cli.py'))
    DRIVER = QuickUsb
    IS_SIMULATING = False
    USE_HANDSHAKING = True
    HAS_IO_PORT = True

    CHUNKSIZE = 1024 * 1024  # 1MB
    MAX_CHUNKSIZE = 16 * 1024 * 1024  # 16MB

    STATE_FILE = "xcam_rack_state.txt"
    # This should either be "xcam_state_vtg_ccd273.txt", or "xcam_state_vtg_ccd204.txt"
    # dependent on which voltage labels are to be used based on CCD204 or CCD273
    VOLT_FILE = "xcam_state_vtg_ccd273.txt"
    DSP_FILE = r"C:\ccd\Sequence\XE164v01\xe164v01.dex"
    DATA_FILE = "data.raw"

    CMD_RESET_FIFO = (0x07, 0x0f)
    CMD_NORMAL = (0xFE, 0xFF)

    CMD_CLOCK_VOLTAGE = 0x01  # cmd, addr, lsb, msb
    CMD_BIAS_VOLTAGE = 0x02  # cmd, addr, lsb, msb
    CMD_POWER = 0x03  # cmd, val
    CMD_LOAD_MEM_PA = 0x04
    CMD_LOAD_MEM_DA = 0x05
    CMD_LOAD_MEM_ADDR = 0x06

    CMD_PARAM = 0x0b  # cmd, addr, lsb, msb
    CMD_GAIN = 0x0c  # cmd, val
    CMD_ACQUIRE = 0x10  # cmd rows[lsb], rows[msb], cols[lsb], cols[msb]
    CMD_VERSION = 0x12
    CMD_CANCEL = 0x14

    PORT_A = 0x00
    PORT_B = 0x01
    PORT_C = 0x02

    STATE_IDLE = 0
    STATE_INTEGRATING = 1
    STATE_READOUT = 2
    STATE_CANCEL = 3
    STATE_CLEARING_CHARGE = 4
    STATE_DATA_READY = 5
    STATE_ACQUIRE = 6
    STATE_INITIALIZING = 7
    STATE_ERROR = -1

    PP_DATA = 0x378
    PP_STATUS = 0x379
    PP_CONTROL = 0x37a


class ParallelPortSimulator(object):

    class IOPort(object):
        def __init__(self):
            self._state = {XCamConst.PP_DATA: 0, XCamConst.PP_STATUS: 0, XCamConst.PP_CONTROL: 0}
            self._useRandom = False

        def Inp32(self, addr):
            if addr == XCamConst.PP_STATUS and self._useRandom:
                self._state[addr] = int(random.random() * 255)
            return self._state[addr]

        def Out32(self, addr, val):
            self._useRandom = (addr == XCamConst.PP_CONTROL and val & 0x1)
            self._state[addr] = val
            return 0

    inpout32 = IOPort()


class EventHandler(object):

    def __init__(self, evt, handler, args=None, key=None, async=False):
        self._event = evt
        self._handler = handler
        self._args = args
        self._enabled = True
        self._key = key
        self._async = async

    def set_key(self, key):
        self._key = key

    def set_args(self, args):
        self._args = args

    def is_key(self, key):
        return self._key == key

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False

    def notify(self, evt):
        print("EventHandler.notify", evt, self._event, self._enabled, self._async)
        if self._event == evt or self._event is None or self._event == -1:
            if self._enabled:
                if self._args is None:
                    self._args = []

                if self._async:
                    th = threading.Thread(target=self._handler, args=self._args)
                    th.start()
                else:
                    self._handler(*self._args)

    @staticmethod
    def Notify(evt, event_handlers):
        for handler in event_handlers:
            handler.notify(evt)

    @staticmethod
    def Find(key, event_handlers):
        for handler in event_handlers:
            if handler.is_key(key):
                return handler


class Simulator(object):

    class QuickUsbSim(object):
        def __init__(self):
            self._currentCmd = 0
            self._bufSizes = []

        @property
        def Make(self):
            return 1, "Bitwise Systems (SIM)"

        @property
        def Model(self):
            return 1, "QuickUSB QUSB2 Module v2.11rc7 (FIFO Handshake)"

        @property
        def Serial(self):
            return 1, "4633"

        @property
        def lastError(self):
            return 0

        def Close(self):
            return 1,

        def SetTimeout(self, _timeout):
            return 1,

        def WriteSetting(self, _addr, _val):
            return 1,

        def WritePortDir(self, _addr, _val):
            return 1,

        def WritePort(self, _port, byte, _len):
            # TODO: flaky!!
            if _port == XCamConst.PORT_A and byte == XCamConst.CMD_VERSION or byte == XCamConst.CMD_ACQUIRE:
                self._currentCmd = byte
            return 1,

        def FindModules(self):
            return 1, ["QUSB-0"]

        def Open(self, _name):
            return 1,

        def ReadData(self, buf, n):
            if self._currentCmd == XCamConst.CMD_VERSION:
                v = ("%-"+str(n)+"s") % "  XCAM V3.0"
                buf.extend([ord(c) for c in v])

            return 1, n

        def ReadDataAsync(self, buf, n):
            self._bufSizes.append(n)
            return 1, n

        def AsyncWait(self, buf, n):
            n = self._bufSizes.pop(0)
            return 1, n


    @staticmethod
    def Error(_err):
        return "ok"

    @staticmethod
    def CreateByteBuffer(n):
        if n > 100:
            return " " * n
        else:
            return []

    @staticmethod
    def QuickUsb():
        return Simulator.QuickUsbSim()


class XCamException(Exception):
    """ exception thrown by the XCam class """

    def __init__(self, msg, err=-1):
        """ initializer """
        super(XCamException, self).__init__()
        self._msg = msg
        self._err = err

    def __str__(self):
        """ human readable format overloaded operator """
        s = self.__class__.__name__
        s += ": " + self._msg + "(" + str(self._err) + ")"
        return s

    def get_error_code(self):
        return self._err


class QuickUSBException(XCamException):
    """ exception due to QuickUSB interaction  """

    def __init__(self, dev, msg=""):
        """ constructor """
        super(QuickUSBException, self).__init__(msg + str(QuickUsb.Error(dev.lastError)), dev.lastError)


class VoltageOutOfRangeException(XCamException):
    """ exception due to QuickUSB interaction  """

    def __init__(self, key, val, rng):
        """ constructor """
        super(VoltageOutOfRangeException, self).__init__("Voltage %s(%s) out of range %s" % (key, str(val), str(rng)))


class ParamRangeException(XCamException):
    """ exception due to QuickUSB interaction  """

    def __init__(self, key, val, rng):
        """ constructor """
        if isinstance(key, int):
            key = Param.get_key(key)

        if rng is None:
            rng_str = "None"
        elif len(rng) > 4:
            rng_str = "[%d ... %d]" % (rng[0], rng[-1])
        else:
            rng_str = str(rng)

        super(ParamRangeException, self).__init__("Param %s(%s) out of range %s" % (key, str(val), rng_str))


class ADUValue(object):

    def __init__(self, key, label, addr, adu, calibration):
        self._key = key
        self._label = label
        self._addr = int(addr)
        self._adu = int(adu)
        self._cal = float(calibration)

    @property
    def calibration(self):
        return self._cal

    @property
    def label(self):
        return self._label

    @property
    def key(self):
        return self._key

    @property
    def command(self):
        if self._key.startswith('vclk_'):
            return XCamConst.CMD_CLOCK_VOLTAGE

        if self._key.startswith('vbias_'):
            return XCamConst.CMD_BIAS_VOLTAGE

        raise KeyError("ADUValue.command invalid key:" + self._key)

    @property
    def address(self):
        return self._addr

    def __int__(self):
        return self._adu

    def __float__(self):
        return self.get_value()

    def set_adu(self, adu):
        self._adu = int(adu)

    def get_adu(self):
        return self._adu

    def set_value(self, val):
        self._adu = int(round(float(val) / self._cal))

    def get_value(self):
        return float(self._adu) * self._cal

    def adu2volt(self, adu):
        return float(adu) * self._cal

    def is_key(self, key):
        if self._key == key:
            return True
        else:
            return False


class VoltageFile(object):

    def __init__(self, voltage_path=None):
        self._values = []
        self._iter_index = 0
        self._file = ''
        if voltage_path:
            self.load(voltage_path)

    @property
    def filename(self):
        return self._file

    def __iter__(self):
        self._iter_index = -1
        return self

    def __next__(self):
        return self.next()

    def next(self):
        self._iter_index += 1
        if self._iter_index < len(self._values):
            return self._values[self._iter_index]
        else:
            raise StopIteration

    def find(self, cmd, addr):
        for adu in self._values:
            if adu.command == cmd and adu.address == addr:
                return adu
        s = "VoltageFile.find: "
        s += "Cound not locate ADU instance. cmd=%d, addr=%02x" % (cmd, addr)
        raise KeyError(s)

    def find_by_key(self, key):
        if isinstance(key, str):
            for val in self._values:
                if val.is_key(key):
                    return val
        else:
            if 1 <= key < len(self._values):
                return self._values[key]

        raise KeyError("VoltageFile.find_by_key could not find key: " + key)

    def match_key(self, crit, cmd=None):
        result = []
        if crit:  # must be non-empty string
            if '1' <= crit <= '8':
                if cmd == XCamConst.CMD_CLOCK_VOLTAGE:
                    crit = 'vclk_' + crit + '_'
                elif cmd == XCamConst.CMD_BIAS_VOLTAGE:
                    crit = 'vclk_' + crit + '_'
                else:
                    crit = '_' + crit + '_'

            if crit.startswith('V'):
                crit = crit[1:]  # Remove Voltage prefix

            for adu in self._values:
                if crit.lower() in adu.key.lower():
                    if cmd is None:
                        result.append(adu.key)
                    elif adu.command == cmd:
                        result.append(adu.key)

        return result

    def load(self, fpath):
        """
        Typical 204 CCD file format::

            Variable  Calibration Value
            IG/DG/F3    .085      87
            Image       .085     111
            Serial      .085     111
            Reset       .085      71
            Vspr        .085       0
            Vspr        .117       0
            Vodef       .133     199
            Vrdef       .117     128
            Vddef       .117     205
            Vog2        .117      34
            Vog1         .11      27
            Vss         .117       0
            Vid         .117     205
            Vspr        .133       0


        Typical 273 CCD file format::

            Variable  Calibration Value
            SW/DG/R3    .085     119
            Image       .085     118
            Serial      .085     106
            Reset       .085     106
            TGA/TGD     .085     129
            Vspr        .117       0
            VodEF       .133     206
            Vrd         .117     139
            Vdd/id      .117     222
            Vog         .117      17
            Vig1         .11      64
            Vss         .117       0
            Vig2        .117      34
            VodGH       .133     206

        """

        # settings_voltages.py
        keys204 = [
            # '',                # line  0
            'vclk_1_ig_dg_f3',   # line  1 IG/DG/F3 index=1, addr=0x02(2)
            'vclk_2_image',      # line  2 Image    index=2, addr=0x04(4)
            'vclk_3_serial',     # line  3 Serial   index=3, addr=0x08(8)
            'vclk_4_reset',      # line  4 Reset    index=4, addr=0x10(16)
            'vclk_5_vspr1',      # line  5 Vspr     index=5, addr=0x20(32)
            'vclk_6_vspr2',      # line  6 Vspr     index=6, addr=0x40(64)

            'vbias_1_odef',      # line  7 Vodef    index=0, addr=0x01(1)
            'vbias_2_rdef',      # line  8 Vrdef    index=1, addr=0x02(2)
            'vbias_3_ddef',      # line  9 Vddef    index=2, addr=0x04(4)
            'vbias_4_og2',       # line 10 Vog2     index=3, addr=0x08(8)
            'vbias_5_og1',       # line 11 Vog1     index=4, addr=0x10(16)
            'vbias_6_ss',        # line 12 Vss      index=5, addr=0x20(32)
            'vbias_7_id',        # line 13 Vid      index=6, addr=0x40(64)
            'vbias_8_vspr',      # line 14 Vspr     index=7, addr=0x80(128)
        ]

        # settings_voltages_ccd273.py
        keys270 = [
            # '',                # line  0
            'vclk_1_sw_dg_r3',   # line  1 IG/DG/F3 index=1, addr=0x02(2)
            'vclk_2_image',      # line  2 Image    index=2, addr=0x04(4)
            'vclk_3_serial',     # line  3 Serial   index=3, addr=0x08(8)
            'vclk_4_reset',      # line  4 Reset    index=4, addr=0x10(16)
            'vclk_5_tg',         # line  5 Vspr     index=5, addr=0x20(32)
            'vclk_6_vspr1',      # line  6 Vspr     index=6, addr=0x40(64)

            'vbias_1_od',        # line  7 Vodef    index=0, addr=0x01(1)
            'vbias_2_rd',        # line  8 Vrdef    index=1, addr=0x02(2)
            'vbias_3_dd_id',     # line  9 Vddef    index=2, addr=0x04(4)
            'vbias_4_og',        # line 10 Vog2     index=3, addr=0x08(8)
            'vbias_5_ig',        # line 11 Vog1     index=4, addr=0x10(16)
            'vbias_6_ss',        # line 12 Vss      index=5, addr=0x20(32)
            'vbias_7_spr2',      # line 13 Vid      index=6, addr=0x40(64)
            'vbias_8_spr3',      # line 14 Vspr     index=7, addr=0x80(128)
        ]

        # settings_voltages_ccd273.py
        keys273 = [
            # '',                # line  0
            'vclk_1_dg_efgh3',   # line  1 IG/DG/F3 index=1, addr=0x02(2)
            'vclk_2_image',      # line  2 Image    index=2, addr=0x04(4)
            'vclk_3_serial',     # line  3 Serial   index=3, addr=0x08(8)
            'vclk_4_reset',      # line  4 Reset    index=4, addr=0x10(16)
            'vclk_5_tga_tgd',    # line  5 Vspr     index=5, addr=0x20(32)
            'vclk_6_vspr2',      # line  6 Vspr     index=6, addr=0x40(64)

            'vbias_1_od_ef',     # line  7 Vodef    index=0, addr=0x01(1)
            'vbias_2_rd',        # line  8 Vrdef    index=1, addr=0x02(2)
            'vbias_3_dd_id',     # line  9 Vddef    index=2, addr=0x04(4)
            'vbias_4_og',        # line 10 Vog2     index=3, addr=0x08(8)
            'vbias_5_ig1',       # line 11 Vog1     index=4, addr=0x10(16)
            'vbias_6_ss',        # line 12 Vss      index=5, addr=0x20(32)
            'vbias_7_ig2',       # line 13 Vid      index=6, addr=0x40(64)
            'vbias_8_od_gh',     # line 14 Vspr     index=7, addr=0x80(128)
        ]

        keys47_20 = [
            # '',                # line  0
            'vclk_1_DG_R3',      # line  1 IG/DG/F3 index=1, addr=0x02(2)
            'vclk_2_I-S',        # line  2 Image    index=2, addr=0x04(4)
            'vclk_3_serial',     # line  3 Serial   index=3, addr=0x08(8)
            'vclk_4_reset',      # line  4 Reset    index=4, addr=0x10(16)
            'vclk_5_not-used',   # line  5 Vspr     index=5, addr=0x20(32)
            'vclk_6_not-used',   # line  6 Vspr     index=6, addr=0x40(64)

            'vbias_1_OD-L_ABD',  # line  7 Vodef    index=0, addr=0x01(1)
            'vbias_2_RD',        # line  8 Vrdef    index=1, addr=0x02(2)
            'vbias_3_not-used',  # line  9 Vddef    index=2, addr=0x04(4)
            'vbias_4_OG',        # line 10 Vog2     index=3, addr=0x08(8)
            'vbias_5_ABG',       # line 11 Vog1     index=4, addr=0x10(16)
            'vbias_6_ss',        # line 12 Vss      index=5, addr=0x20(32)
            'vbias_7_not-used',  # line 13 Vid      index=6, addr=0x40(64)
            'vbias_8_OD-R',      # line 14 Vspr     index=7, addr=0x80(128)
        ]

        if "204" in fpath:
            keys = keys204
        elif "270" in fpath:
            keys = keys270
        elif "47-20" in fpath:
            keys = keys47_20
        else:
            keys = keys273

        if not os.path.exists(fpath):
            if os.path.exists(fpath + '.cpy'):
                shutil.copy2(fpath + '.cpy', fpath)

        self._file = fpath
        if not os.path.exists(self._file):
            logging.getLogger('xcam').warning('Cannot find %s', fpath)
            return

        with open(fpath) as f:
            expr = re.compile('(.+[^\s])\s+(\.\d+)\s+(\d+)')
            f.readline()  # skip header line
            for i, line in enumerate(f.readlines()):
                parts = re.findall(expr, line)
                if len(parts):
                    label, cal, adu = parts[0]
                    key = keys[i]
                    if i < 6:
                        addr = 1 << i
                    else:
                        addr = 1 << (i-6)
                    # print key, label, addr
                    self._values.append(ADUValue(key, label, addr, adu, cal))

    def save(self, fpath=None):
        if fpath:
            self._file = fpath

        with open(self._file, 'w') as f:
            f.write("%-10s%-12s%-6s\n" % ("Variable", "Calibration", "Value"))
            for adu in self._values:
                row = (adu.label, str(adu.calibration).strip('0'), int(adu))
                f.write("%-11s%5s%8d \n" % row)


class DSPFile(object):
    """ converts the compiled DSP (.dex) sequencer file into a byte sequence
    that can then be uploaded via the QuickUSB link to the ADSP-2181 on the
    XCam rack.
    """

    def __init__(self, seq_path=None):
        self._bytes = []
        self._file = ''
        self._checksum = 0
        if seq_path:
            self.load(seq_path)

    @property
    def checksum(self):
        return self._checksum

    @property
    def bytes(self):
        return self._bytes

    @property
    def filename(self):
        return self._file

    def load(self, seq_path):
        self._file = seq_path
        self._bytes, self._checksum = DSPFile.get_bytes(seq_path)

    @staticmethod
    def get_bytes(seq_path):
        """

        Protocol::
            0x04  ,                            (in PA section)
            [paN1], [paN0],  0x01, 0x00        (number of PA 24bit words)
            [hex1], [hex0], [hex2]             (1st program byte word, 24bits)
            ...                                (Nth program byte word)
            0x05  ,                            (in DA section)
            [daN1], [daN0]                     (number of DA 16bit words)
            [hex1], [hex0]                     (1st data byte word, 16bits)
            ...                                (Nth data byte word)
            0x06  ,                            (in PA memory location)
            [paL1], [paL0], [paL2]

        where::
            xxx0 => MSB
            xxx1 => LSB
            xxx2 => LLSB*

        *only applies to 24bit PA words - the least least significant word

        """
        with open(seq_path) as f:
            skip = 0
            seq = []
            in_pa = False
            in_da = False
            pa_cnt = 0
            da_cnt = 0
            da_cnt_last = 0
            pa_mem_loc = ""
            da_loc = 0
            pa_loc = 0

            checksum = 0
            for line in f:
                if skip:
                    pa_mem_loc = line
                    skip -= 1

                elif line[0] == '#' and in_pa:
                    continue

                elif line[0] == '#' and in_da:
                    in_pa = False
                    in_da = False
                    da_cnt -= 1
                    seq[da_loc+0] = (da_cnt & 0x00ff) >> 0
                    seq[da_loc+1] = (da_cnt & 0xff00) >> 8
                    da_cnt_last = da_cnt
                    da_cnt = 0
                    # print "DA"
                    # for i in range(daLoc, len(seq), 2):
                    #     x0 = seq[i+0]
                    #     x1 = seq[i+1]
                    #     print "0x%04x, %d" % (Byte2Short([x0, x1]), ((i-daLoc)/2)-2)

                elif "@DA\n" in line:
                    in_da = True
                    in_pa = False
                    seq.append(XCamConst.CMD_LOAD_MEM_DA)  # load DA command
                    da_loc = len(seq)
                    seq.append(0x00)  # lo DA line count
                    seq.append(0x00)  # hi DA line count

                elif "@PA\n" in line:
                    in_pa = True
                    in_da = False
                    skip = 2
                    seq.append(XCamConst.CMD_LOAD_MEM_PA)  # load PA command
                    pa_loc = len(seq)  # location where the PA word count is placed
                    seq.append(0x00)  # lo PA line count
                    seq.append(0x00)  # hi PA line count
                    seq.append(0x01)  # fixed
                    seq.append(0x00)  # fixed

                elif in_pa:
                    seq.append(int(line[2:4], 16))
                    seq.append(int(line[0:2], 16))
                    seq.append(int(line[4:6], 16))
                    pa_cnt += 1

                elif in_da:
                    val = int(line, 16)
                    if da_cnt > 0:
                        checksum ^= val
                    seq.append(int(line[2:4], 16))
                    seq.append(int(line[0:2], 16))
                    # print "%04X" % val, "%04X" % checksum, "0x%02x %04X" %
                    # (daCnt, ((seq[len(seq)-1] << 8) + (seq[len(seq)-2] << 0)))
                    da_cnt += 1

            seq.append(XCamConst.CMD_LOAD_MEM_ADDR)  # load PA at memory location command
            seq.append(int(pa_mem_loc[2:4], 16))
            seq.append(int(pa_mem_loc[0:2], 16))
            seq.append(int(pa_mem_loc[4:6], 16))
            seq[pa_loc+0] = (pa_cnt & 0x00ff) >> 0
            seq[pa_loc+1] = (pa_cnt & 0xff00) >> 8

        print("Parsed DSP file: PA words=%d, DA words=%d" % (pa_cnt, da_cnt_last))
        with open('loaded_bytes.txt', 'w') as file_obj:
            file_obj.write(str(seq))

        return seq, checksum


class RackState(object):
    """
    This class saves the state of the XCam rack to a file when it is commanded,
    and provides high level function calls to query the last know state of
    voltages, gain, delays, and power. This class DOES NOT command the rack
    it only keeps track of the state, since the XCam rack does not provide
    any functionality to query the state parameters.
    """

    def __init__(self, fpath):
        self._path = fpath
        self._commands = {}

        if os.path.exists(self._path):
            self.load(self._path)

    @property
    def commands(self):
        return self._commands

    def get_power(self):
        return self._commands.get(XCamConst.CMD_POWER, None)

    def get_gain(self):
        return self._commands.get(XCamConst.CMD_GAIN, 0)

    def get_voltage_bias(self, addr):
        return Readout.byte2short(self._commands.get((XCamConst.CMD_BIAS_VOLTAGE, addr), None))

    def get_voltage_clock(self, addr):
        return Readout.byte2short(self._commands.get((XCamConst.CMD_CLOCK_VOLTAGE, addr), None))

    def get_int_time(self):
        int_time = self.get_param(Param.addr_int_time)
        int_unit = self.get_param(Param.addr_int_units)

        if int_unit == 1:
            exp_time = float(int_time) * (1.0/10.0)
        else:
            exp_time = float(int_time) * (1.0/100.0)

        return exp_time

    def get_param(self, addr):
        pair = self._commands.get((XCamConst.CMD_PARAM, addr), None)
        if pair is None:
            return Param.get_default_value(addr)
        val = Readout.byte2short(pair)
        if addr == Param.addr_trappump_cycles or addr == Param.addr_ser_trappump_cycles:
            val *= 10
        return val

    def load(self, rack_state_path=None):
        if rack_state_path:
            self._path = rack_state_path

        if os.path.exists(self._path):
            with open(self._path) as file_obj:
                s = ''.join(file_obj.readlines())
                try:
                    self._commands = eval(s)
                except SyntaxError as ex:
                    print("RackState.load exception: %s" % str(ex))
                self._remove_unwanted_keys()

    def save(self, fpath=None):
        self._remove_unwanted_keys()
        if fpath:
            self._path = fpath

        with open(self._path, 'w') as file_obj:
            file_obj.write(str(self._commands))

    def _remove_unwanted_keys(self):
        # do not save the parameters that are used to send signals
        bad_keys = [
            (XCamConst.CMD_PARAM, Param.addr_cancel),
            (XCamConst.CMD_PARAM, Param.addr_send_sync),
            (XCamConst.CMD_PARAM, Param.addr_dump_memory),
            (XCamConst.CMD_PARAM, Param.addr_pause_dsp),
            (XCamConst.CMD_PARAM, Param.addr_test_pf6_input),
            (XCamConst.CMD_PARAM, Param.addr_fpr_eper_delay),
        ]
        for key in bad_keys:
            if key in self._commands:
                del self._commands[key]

    def update(self, key, arg):
        self._commands[key] = arg
        self._remove_unwanted_keys()
        self.save()


class Param(int):

    addr_checksum             =  0 # [0-0xffff]
    addr_pre_clamp_delay      =  1 # [1..16383]
    addr_pre_int2_delay       =  2 # [1..16383]
    addr_pixel_int_time       =  3 # [1..16383]
    addr_serial_clk_stretch   =  4 # [1..16383]
    addr_parallel_clk_stretch =  5 # [1..16383]
    addr_injection_period     =  6 # [1..16383]
    addr_injection_lines      =  7 # [1..16383]
    addr_serial_clk_overlap   =  8 # [1..16383]
    addr_bin_number           =  9 # [1..16383]
    addr_cols                 = 10 # [4..4600]
    addr_rows                 = 11 # [4..4600]
    addr_stretch_phase1       = 12 # [1..16383]
    addr_stretch_phase2       = 13 # [1..16383]
    addr_stretch_phase3       = 14 # [1..16383]
    addr_int_time             = 15 # [1 ... 65535] => [0.01s ... 6553.5s]
    addr_version              = 16 # [1 ... 100]
    addr_cancel               = 17 # [1] => trigger cancel
    addr_readout_dir          = 18 # [0, 1, 2, 3] => [norm, revm fg, eh]
    addr_dump_memory          = 19 # [0] => trigger memory dump via print port
    addr_dummy_pix_readout    = 20 # [0, 1] => [-, dummy pixel readout]
    addr_frame_erasure        = 21 # [0, 1] => [-, erasure]
    addr_parallel_dir         = 22 # [0, 1] => [forward, backward]
    addr_pause_dsp            = 23 # [0, 1] => [-, pause]
    addr_dump_last_lines      = 24 # [0, 4600] =>
    addr_test_pf6_input       = 25 # [0, 1] => [-, test]

    addr_readout_sync         = 26 # [0, 1] => [-, wait]
    addr_wait_time            = 27 # [1 ... 16383] => ms
    addr_send_sync            = 28 # [0, 1] => [off, on]
    addr_channels             = 29 # [1, 2, 4]
    addr_trappump_cycles      = 30 # [0..16383]
    addr_image_clk_int        = 31 # [0 ... 0xffff]
    addr_serial_first_pixel   = 32 # [0, 1] => [off, on]
    addr_card_num             = 33 # [1,2,3,4,5]
    addr_ser_trappump_cycles  = 34 # [0..16383]
    addr_slosh_delay          = 35 # [1..16383]
    addr_slosh_enable         = 36 # [0, 1]
    addr_ci_frame_enabled     = 37 # [0, 1]

    addr_int_units            = 64 # [0, 1] => [0.01s, 0.1s] resolution
    addr_frame_tx_count       = 65 # [0, 4600] (this will be more than 1 later)
    addr_parallel_phases      = 68 # [0, 1] => [4 phase, 3 phase (cheops)]
    addr_fpr_eper_delay       = 69 # [0, 1000] => [delay in sec before parallel fpr readout]
    addr_eper_enabled         = 70 # [0, 1] => [enable serial extended pixel edge response]
    addr_clock_config         = 71 # [0, 1, 2, 3, 4]

    @staticmethod
    def get_addr_atts(addr):
        cntrRange = range(1, 16384, 1)
        vals = {                            # (def, valid range)
            Param.addr_checksum             : (  0, range(0, 65536)),
            Param.addr_pre_clamp_delay      : ( 12, cntrRange),
            Param.addr_pre_int2_delay       : (  8, cntrRange),
            Param.addr_pixel_int_time       : ( 40, cntrRange),
            Param.addr_serial_clk_stretch   : ( 16, cntrRange),
            Param.addr_parallel_clk_stretch : (150, cntrRange),
            Param.addr_injection_period     : (  1, cntrRange),
            Param.addr_injection_lines      : (  1, cntrRange),
            Param.addr_serial_clk_overlap   : (  2, cntrRange),
            Param.addr_bin_number           : (  1, range(1, 17)),
            Param.addr_cols                 : (4600, range(8, 9202, 2)),
            Param.addr_rows                 : (1600, range(8, 9202, 2)),
            Param.addr_stretch_phase1       : (  1, cntrRange),
            Param.addr_stretch_phase2       : (  1, cntrRange),
            Param.addr_stretch_phase3       : (  1, cntrRange),
            Param.addr_int_time             : (  1, range(1, 65536)),
            Param.addr_version              : (  0, [0, 100]),
            Param.addr_cancel               : (  0, [0, 1]),
            Param.addr_readout_dir          : (  0, [0, 1, 2, 3]),
            Param.addr_dump_memory          : (  0, range(-1, 1024)),
            Param.addr_dummy_pix_readout    : (  0, [0, 1]),
            Param.addr_frame_erasure        : (  0, [0, 1]),
            Param.addr_parallel_dir         : (  0, [0, 1]),
            Param.addr_dump_last_lines      : (  0, range(0, 4601, 1)),
            Param.addr_pause_dsp            : (  0, [0, 1]),
            Param.addr_test_pf6_input       : (  0, [0, 1]),
            Param.addr_readout_sync         : (  0, [0, 1]),
            Param.addr_wait_time            : (500, cntrRange),
            Param.addr_send_sync            : (  1, [0, 1]),
            Param.addr_channels             : (  4, [1, 2, 4]),
            Param.addr_trappump_cycles      : (  0, range(0, 16384, 1)),
            Param.addr_image_clk_int        : (  0, None),
            Param.addr_serial_first_pixel   : (  0, [0, 1]),
            Param.addr_int_units            : (  0, [0, 1]),
            Param.addr_frame_tx_count       : (  0, range(0, 4600, 1)),
            Param.addr_parallel_phases      : (  0, [0, 1]),
            Param.addr_fpr_eper_delay       : (  0, range(0, 4600, 1)),
            Param.addr_card_num             : (  4, [1, 2, 3, 4, 5, 6, 7, 8]),
            Param.addr_ser_trappump_cycles  : (  0, range(0, 16384, 1)),
            Param.addr_slosh_delay          : (  0, cntrRange),
            Param.addr_slosh_enable         : (  0, [0, 1]),
            Param.addr_ci_frame_enabled     : (  0, [0, 1]),
            Param.addr_eper_enabled         : (  0, [0, 1]),
            Param.addr_clock_config         : (  0, [0, 1, 2, 3, 4]),
        }
        if addr in vals:
            return vals[addr]
        else:
            print("ERROR: xcam.Params.get_addr_atts could not find address %d" % addr)
            return 0, None

    @staticmethod
    def get_default_value(addr):
        addr_atts = Param.get_addr_atts(addr)
        return addr_atts[0]

    @staticmethod
    def get_range(addr):
        addr_atts = Param.get_addr_atts(addr)
        return addr_atts[1]

    @staticmethod
    def get_key(addr):
        self = Param()
        try:
            return [k for k, v in self.__class__.__dict__.items() if v == int(addr)].pop()
        except IndexError:
            return None

    @staticmethod
    def find_key(crit):
        crit = crit.lower().replace('-', '_')
        for key, addr in Param.__dict__.items():
            if crit == str(addr):
                return key
            if 'addr_' + crit == key:
                return key
            if crit == key:
                return key

    def __str__(self):
        keys = [k for k, v in self.__class__.__dict__.items() if v == int(self)]
        if len(keys) > 0:
            return "%s.%s" % (self.__class__.__name__, keys[0])
        else:
            return "%s.%s" % (self.__class__.__name__, str(int(self)))


class XCam(object):

    def __init__(self, _addr=None):
        """ constructor """
        self._com = None
        self._voltages = None
        self._rack = None
        self.__state = XCamConst.STATE_IDLE
        self._dsp = None
        self._timeAcquire = 0
        self._timeReadout = 0
        self._timeClear = 0
        self._timeInt = 0
        self._headers = {}
        self._timestamp = ''
        self._eventHandlers = []
        self._channels = 1
        self._bits = 16
        self._asyncReadout = False
        self._voltageRangeChecks = {}
        self._controlInternalShutter = False  # TODO: this may require a re-think
        self._shutState = False
        self._serialEPERMode = False
        self._mutex = threading.Lock()

        self.open()

    @property
    def voltages(self):
        return self._voltages

    def set_event_handler(self, state=None, callback=None, args=None, key=None, enabled=None, async=False):
        evt_handler = None
        if key:
            evt_handler = EventHandler.Find(key, self._eventHandlers)

        if evt_handler is None:
            evt_handler = EventHandler(state, callback, args, key, async)
            self._eventHandlers.append(evt_handler)

        if args is not None:
            evt_handler.set_args(args)

        if enabled is None:
            pass
        elif enabled:
            evt_handler.enable()
        else:
            evt_handler.disable()

        return evt_handler

    def set_channels(self, ch):
        if isinstance(ch, str):
            channel_map = {
                "16Q": 4,
                "16D": 2,
                "16S": 1,
                "14Q": 4,
                "14D": 2,
                "14S": 1,
            }
            bits = int(ch[:-1])
            ch = channel_map[ch]
        else:
            bits = self._bits  # use the original value

        self._channels = ch
        self._bits = bits
        self.set_param(Param.addr_channels, ch)

    def set_async_readout(self, is_async):
        self._asyncReadout = is_async

    def remove_header(self, key):
        if key in self._headers:
            del self._headers[key]

    def set_header(self, key, val):
        log = logging.getLogger("xcam")
        log.info('XCam.set_header: %s=%s' % (key, repr(val)))
        self._headers[key] = val

    def get_header(self, key, default_value=None):
        if default_value is None:
            return self._headers[key]  # raises a KeyError if key does not exist
        else:
            return self._headers.get(key, default_value)

    @property
    def state(self):
        return self.__state

    def _set_state(self, new_state):
        self.__state = new_state
        EventHandler.Notify(new_state, self._eventHandlers)

    @property
    def rack(self):
        return self._rack

    @property
    def channels(self):
        return self._channels

    @property
    def inttime(self):
        return self.rack.get_int_time()
        # return self._timeInt

    @property
    def acqtime(self):
        return self._timeAcquire

    @property
    def dspfile(self):
        if self._dsp:
            return self._dsp.filename
        else:
            return ''

    @property
    def checksum(self):
        return self._dsp.checksum

    def init_rack(self, state_file=XCamConst.STATE_FILE, volt_file=XCamConst.VOLT_FILE, dsp_file=XCamConst.DSP_FILE):
        self._set_state(XCamConst.STATE_INITIALIZING)
        log = logging.getLogger("xcam")

        log.info("XCam.init_rack: dsp file: %s" % dsp_file)
        self._dsp = DSPFile(dsp_file)

        log.info("XCam.init_rack: state file: %s" % state_file)
        self._rack = RackState(state_file)

        log.info("XCam.init_rack: volt file: %s" % volt_file)
        self._voltages = VoltageFile(volt_file)

        for adu in self._voltages:
            values = self._rack.commands.get((adu.command, adu.address))
            if values:
                log.info("XCam.init_rack: presetting : %s" % adu.key)
                adu.set_adu(Readout.byte2short(values))

    def init_usb_controller(self):
        """ Open communication and configure the USB settings. """

        self.open()

        dev = self._com

        # ---------------
        # USB controller mode

        # Reference: Page 54 of the "QuickUSB User Guide.pdf"
        # SETTING_FIFO_CONFIG:
        #  Bits 0+1: 10: GPIF Master mode
        #  Bit 5 : 1=Drive the IFCLK pin
        #  Bit 6 : 1=48MHz
        #  Bit 7 : 1=Internal clock
        dev.WriteSetting(3, 0x00E2)  # master mode

        # SETTING_DATAADDRESS:
        #  Bit 15: 1=Don't increment address bus
        #  Bit 14: 1=disable address bus (port C[7:0] and E[7] may be used as
        #          general purpose I/O)
        dev.WriteSetting(2, 0xC000)  # disable address bus and auto-increment

        # SETTING_WORDWIDE:
        #  Bit 0: 1 = 16 bits
        dev.WriteSetting(1, 0x0001)  # data width 16 bits

        # ---------------
        # port directions
        dev.WritePortDir(0, 0xFF)   # port A all o/p
        dev.WritePortDir(2, 0x0F)   # port C low nibble o/p
        dev.WritePortDir(4, 0x00)   # port E all i/p

        # ---------------
        # initialisation
        dev.WritePort(2, 0x01, 1)  # set strobe high & reset fifos
        dev.WritePort(2, 0x0F, 1)  # set strobe high

        dev.Close()

    def is_open(self):
        return self._com is not None

    def open(self):
        """
        Open the QuickUSB link for communication. If it is already open
        the existing link will closed and reopened.
        """
        if self._com:
            self._com.Close()

        dev = QuickUsb.QuickUsb()

        (ok, names) = dev.FindModules()
        if not ok:
            raise QuickUSBException(dev)

        (ok,) = dev.Open(names[0])
        if not ok:
            raise QuickUSBException(dev)

        self._com = dev
        self.__state = XCamConst.STATE_IDLE

    def close(self):
        """ Close QuickUSB device """
        dev = self._com
        if dev is not None:
            # self.cancel()  # cancel any exposure that may be running
            (ok,) = dev.Close()
            if not ok:
                if platform.architecture()[0] == '32bit':
                    raise QuickUSBException(dev)
                else:
                    # TODO: 64bit quick usb issue with SetTimeout
                    print(str(QuickUSBException(dev)))

        self._com = None

    def reset_fifo(self):
        """ Reset the XCAM rack's FIFO for data readout. This is currently
        only used for XCAM version and image data retrieval. """
        dev = self._com
        dev.WritePort(XCamConst.PORT_C, XCamConst.CMD_RESET_FIFO, len(XCamConst.CMD_RESET_FIFO))

    def is_busy(self, raise_error=False, cmd=-1):
        err_states = [XCamConst.STATE_INTEGRATING, XCamConst.STATE_READOUT]
        if cmd != XCamConst.CMD_CANCEL and self.__state in err_states:
            if not raise_error:
                return True
            msg = "Readout is taking place. Ignoring command 0x%02x" % cmd
            log = logging.getLogger("xcam")
            log.error(msg)
            raise XCamException(msg)
        return False

    def write(self, cmd, arg=None):
        """
        XCAM generic commanding. The byte sequence is as follows::

                [0xnn], 0xfe, 0xff

        where::
            0xnn is the sequence of bytes to be written. The 0xfe, 0xff seem
            to act as a terminator. It may also indicate the byte size, I'm
            not sure.

        *arguments*
            ``cmd`` : the sequence of bytes that make up the XCAM command.
                A list, tuple, or int type are allowed.
            ``arg`` : optional. A command byte argument or sequence of bytes.
                A list, tuple, or int type are allowed.

        *raises*
            :class:`QuickUSBException`
        """
        self.is_busy(True, cmd)

        dev = self._com

        if isinstance(cmd, tuple) or isinstance(cmd, list):
            seq = list(cmd)
        else:
            # acceptable types: int, long, str
            seq = [int(cmd)]

        if arg is not None:
            if isinstance(arg, tuple) or isinstance(arg, list):
                seq.extend(arg)
            else:
                seq.append(int(arg))

        for byte in seq:
            (ok,) = dev.WritePort(XCamConst.PORT_A, byte, 1)
            if not ok:
                raise QuickUSBException(dev, "XCam write byte error. ")
            (ok,) = dev.WritePort(XCamConst.PORT_C, XCamConst.CMD_NORMAL, len(XCamConst.CMD_NORMAL))
            if not ok:
                raise QuickUSBException(dev, "XCam write command error. ")

        self._save_command(seq)
        self._log_command(seq)

    def _log_command(self, seq):
        log = logging.getLogger("xcam")
        cmd = seq[0]

        if cmd == XCamConst.CMD_CLOCK_VOLTAGE or cmd == XCamConst.CMD_BIAS_VOLTAGE:
            addr = seq[1]
            lsb = seq[2]
            msb = seq[3]
            val = msb << 8 | lsb
            adu = self._voltages.find(cmd, addr)
            adu.set_adu(val)
            s = "Setting %-15s voltage to %6.3fV. [0x%02X] = %d" \
                % (adu.key, adu.get_value(), adu.address, adu.get_adu())

        elif cmd == XCamConst.CMD_PARAM:
            addr = seq[1]
            lsb = seq[2]
            msb = seq[3]
            val = msb << 8 | lsb
            desc = Param(Param(addr))
            s = "Setting DSP memory address %2d = %3d (%s)." % (addr, val, desc)
            if addr == Param.addr_dump_memory:
                # for clarity skip this logging of memory address
                # (logs may become to verbose)
                return

        elif cmd == XCamConst.CMD_POWER:
            val = seq[1]
            s = "Setting CCD power %d" % val

        elif cmd == XCamConst.CMD_GAIN:
            val = seq[1]
            s = "Setting CCD gain %d" % val

        elif cmd == XCamConst.CMD_LOAD_MEM_PA:
            s = "Uploading DSP sequencer code"

        elif cmd == XCamConst.CMD_VERSION:
            s = "Requesting interface card version"

        elif cmd == XCamConst.CMD_ACQUIRE:
            rlsb = seq[1]
            rmsb = seq[2]
            clsb = seq[3]
            cmsb = seq[4]
            rows = rmsb << 8 | rlsb
            cols = cmsb << 8 | clsb
            s = "Initiating an acquisition. Rows x Cols = %dx%d" % (rows, cols)

        elif cmd == XCamConst.CMD_CANCEL:
            s = "Cancelling acquisition readout due to timeout."

        else:
            s = "Unknown command (%d)" % cmd

        log.info(s)

    def _save_command(self, seq):

        if self._rack is not None:
            if seq[0] in [XCamConst.CMD_CLOCK_VOLTAGE, XCamConst.CMD_BIAS_VOLTAGE, XCamConst.CMD_PARAM]:
                key, arg = (seq[0], seq[1]), (seq[2], seq[3])
            elif seq[0] in [XCamConst.CMD_GAIN, XCamConst.CMD_POWER]:
                key, arg = seq[0], seq[1]
            else:
                key, arg = None, None

            if key is not None:
                self._rack.update(key, arg)

    def cancel_integration(self):
        # send cancel signal to DSP
        self._set_state(XCamConst.STATE_CANCEL)
        self.set_param(Param.addr_cancel, 1)

    def cancel_readout(self):
        self.write(XCamConst.CMD_CANCEL)  # cancel grab if read failed
        # timeout results in next grabs timing out too, unless app is restarted,
        # when normal service is resumed: card_init() is called again in these
        # circumstances to "simulate" app restart
        self.close()
        self.open()
        self.init_usb_controller()

    def get_time_left(self):

        t_dif = 0.0

        if self.state == XCamConst.STATE_INTEGRATING:
            t_past = time.time() - self._timeAcquire
            t_dif = self._timeInt - t_past

        elif self.state == XCamConst.STATE_READOUT:
            t_past = time.time() - self._timeAcquire - self._timeInt
            t_dif = self._timeReadout - t_past

        elif self.state == XCamConst.STATE_CLEARING_CHARGE:
            t_past = time.time() - self._timeClear
            t_dif = t_past

        return t_dif

    def calculate_trap_pumping_time(self):
        """ Count the number of clock cycles (cc) and the final time it quickusb
        readout should be delayed due to trap pump cycling. If many cycles are
        used, than the QuickUSB max timeout of 300 seconds may occur and raise
        an exception in the acquire readout routine.
        NOTE: this is VERY dsp code dependent.
        """
        cols = self.rack.get_param(Param.addr_cols)
        bins = self.rack.get_param(Param.addr_bin_number)
        par_delay = self.rack.get_param(Param.addr_parallel_clk_stretch)
        trap_cycles = self.rack.get_param(Param.addr_trappump_cycles)
        if trap_cycles == 0:
            return 0.0

        # ParallelForward / ParallelBackward
        cc_p = 5 + bins * (1 + 8 * (1 + 2 + 4 + par_delay * 3))
        tpc, cc_pixel, _cc_phase1, _cc_phase2, _cc_phase3 = self.calculate_phases_times()
        cc_i = cc_pixel

        if self._channels != 1:
            cols = cols // 2

        t = tpc * trap_cycles * 2 * ((cols * cc_i) + cc_p)
        return t

    def calculate_phases_times(self):
        """ Count the number of clock cycles (cc) and calculate the pixel
        readout and phase time according to 16bit DSP code.
        NOTE: this is VERY dsp code dependent.
        """
        if self.rack is None:
            return 0, 0, 0, 0, 0

        parm_delay_preclamp = self.rack.get_param(Param.addr_pre_clamp_delay)
        parm_delay_inttime = self.rack.get_param(Param.addr_pixel_int_time)
        parm_delay_preint2 = self.rack.get_param(Param.addr_pre_int2_delay)
        parm_delay_phase1 = self.rack.get_param(Param.addr_stretch_phase1)
        parm_delay_phase2 = self.rack.get_param(Param.addr_stretch_phase2)
        parm_delay_phase3 = self.rack.get_param(Param.addr_stretch_phase3)
        parm_delay_overlap = self.rack.get_param(Param.addr_serial_clk_overlap)

        cc_io_setting = 3  # AR + IO
        cc_delay_over_head = 2  # CNTR + DO...
        tpc = 31.25 / 1e09  # time per clock cycle (s/cc)
        cc_pixel = 15 * cc_io_setting + 10 * cc_delay_over_head + (5 + 6) \
            + 3 * parm_delay_overlap + parm_delay_preclamp \
            + 2 * parm_delay_inttime + parm_delay_preint2 \
            + parm_delay_phase1 + parm_delay_phase2 + parm_delay_phase3 \
            + 1  # NOP on loop

        cc_phase1 = 6 * cc_io_setting + 5 * cc_delay_over_head + 5 \
            + 2 * parm_delay_overlap + parm_delay_preclamp \
            + parm_delay_inttime + parm_delay_phase1

        cc_phase2 = 6 * cc_io_setting + 5 * cc_delay_over_head \
            + 2 * parm_delay_overlap + parm_delay_preint2 \
            + parm_delay_inttime + parm_delay_phase2

        cc_phase3 = 6 * cc_io_setting + 3 * cc_delay_over_head + (6 + 1) \
            + 2 * parm_delay_overlap + parm_delay_phase3

        return tpc, cc_pixel, cc_phase1, cc_phase2, cc_phase3

    def calculate_readout_time(self):
        """ Count the number of clock cycles (cc) and calculate the readout
        time according to 16bit DSP code.
        NOTE: this is VERY dsp code dependent.
        """
        rows = self.rack.get_param(Param.addr_rows)
        cols = self.rack.get_param(Param.addr_cols)
        bins = self.rack.get_param(Param.addr_bin_number)
        par_delay = self.rack.get_param(Param.addr_parallel_clk_stretch)
        # _int_delay = self.rack.get_param(Param.addr_pixel_int_time)
        # _preC_delay = self.rack.get_param(Param.addr_pre_clamp_delay)
        # _preI_delay = self.rack.get_param(Param.addr_pre_int2_delay)
        # ser_1st_pix = self.rack.get_param(Param.addr_serial_first_pixel)
        wait_time = self.rack.get_param(Param.addr_wait_time)
        inject_frame = self.rack.get_param(Param.addr_ci_frame_enabled)
        read_dir = self.rack.get_param(Param.addr_readout_dir)

        ser_trap_pump = self.rack.get_param(Param.addr_ser_trappump_cycles)

        # TODO: add the ser_1st_pix time to the total time

        # clear full serial
        cc_s = 4 + 4600 * (1 + 2 + 1) * 3

        # ParallelForward / ParallelBackward
        cc_p = 5 + bins * (1 + 8 * (1 + 2 + 4 + par_delay * 3))
        tpc, cc_pixel, _cc_phase1, _cc_phase2, _cc_phase3 = self.calculate_phases_times()
        cc_i = cc_pixel

        divider = self._channels
        if self._channels == 4:
            if read_dir & 2:  # test bit 2 readout dir 2: <--FG<--, 3 -->EH-->
                divider = self._channels // 2

        print("calculate_readout_time ccPixel", cc_pixel)
        if self._channels == 4:
            par_rows = rows // 2
        else:
            par_rows = rows

        t = (cc_i * rows * cols) // divider  # pixel readout
        t += cc_p * par_rows  # ParallelFoward/Backward time
        t += 2 * cc_s  # clear full serial
        t += (ser_trap_pump * 2 * (cc_i + 46 + 48)) * par_rows  # serial trap pumping approximation

        t *= tpc  # convert to seconds
        # add the wait time before the DSP starts clocking out the pixels.
        t += float(wait_time) / 1000.0
        t += 0.4  # add 400ms for handshaking and data decoding

        print("calculate_readout_time t", t)
        if inject_frame:
            # charge injected frames are first 'dummy' readout,
            # than 'strobed' readout.
            t *= 2.0
        return t

    def set_int_time(self, int_time_in_sec):
        if int_time_in_sec < 10.0:
            time_units = 0  # 1/100's
            t = int(int_time_in_sec / (1.0/100.0))
        else:
            time_units = 1  # 1/10's
            t = int(int_time_in_sec / (1.0/10.0))

        if t <= 0:
            # NOTE: for sequencer with timer interrupt enabled, this may be 0.
            t = 1  # ensure a positive integer adu time value.

        self.set_param(Param.addr_int_time,  t)
        self.set_param(Param.addr_int_units, time_units)

    def acquire(self, rows=None, cols=None, int_time_in_sec=None, async=None):

        log = logging.getLogger("xcam")

        if int_time_in_sec is not None:
            self.set_int_time(int_time_in_sec)

        if async is not None:
            self._asyncReadout = async

        self.handshake(0)
        if cols:
            self.set_param(Param.addr_cols, cols)
        if rows:
            self.set_param(Param.addr_rows, rows)

        rows = self.rack.get_param(Param.addr_rows)
        cols = self.rack.get_param(Param.addr_cols)
        chns = self.rack.get_param(Param.addr_channels)
        # read_dir_0 = self.rack.get_param(Param.addr_readout_dir)
        # if self._serialEPERMode:
        #     self.set_param(Param.addr_readout_dir, 0) # e/f/g/h readout mode

        rdir = self.rack.get_param(Param.addr_readout_dir)
        if chns == 4:
            if (rdir == 2) or (rdir == 3):
                print("xcam.acquire: 2 x the cols")
                cols *= 2
            # elif self._serialEPERMode and (read_dir_0 == 2) or (read_dir_0 == 3):
            #     cols *= 2
            #     self.set_param(Param.addr_cols, cols*2)

        self._timeInt = self.rack.get_int_time()

        if self.get_header('remove_top_half', False):
            print("removing top half of image mode")
            rows = rows * 2
            self.set_param(Param.addr_rows, rows)

        self._set_state(XCamConst.STATE_ACQUIRE)
        self.reset_fifo()
        arg = (rows & 0xff, (rows >> 8) & 0xff, cols & 0xff, (cols >> 8) & 0xff)
        self.write(XCamConst.CMD_ACQUIRE, arg)

        if self._timeInt > 0.1:
            # wait until the  LED signal is caught.
            # in the case of Erasure, the pre-integration wait time
            # can add up to a few seconds when binning is used.
            timeout = 60.0
            t0 = time.time()
            while time.time() - t0 < timeout:
                if self.get_led_state():
                    break
                time.sleep(0.001)
                if XCamConst.IS_SIMULATING:
                    break
                if not XCamConst.HAS_IO_PORT:
                    break

        self._timeAcquire = time.time()

        self._set_state(XCamConst.STATE_INTEGRATING)

        pre_setup_readout_time = 2.0
        if XCamConst.USE_HANDSHAKING and self.rack.get_param(Param.addr_readout_sync):
            pre_setup_readout_time = 0.0

        if self._timeInt > pre_setup_readout_time:
            pause_time = self._timeInt - pre_setup_readout_time
            t0 = time.time()
            while time.time() - t0 < pause_time:
                time.sleep(0.001)
                if self.state == XCamConst.STATE_CANCEL:
                    self._set_state(XCamConst.STATE_IDLE)
                    return None

        self._set_state(XCamConst.STATE_READOUT)
        self._timeReadout = self.calculate_readout_time()

        trap_time = self.calculate_trap_pumping_time()
        log.info("trap time = %0.1f seconds" % trap_time)
        if trap_time > 2.0:
            # it is critical that the readout starts before the rack starts
            # clocking out the data. Slice off 1 second just to be sure.
            # NOTE: I'm not sure if this applies when handshaking is used.
            #   to be tested.
            trap_time -= 1.0
            self._timeReadout += trap_time
            time.sleep(trap_time)

        log.info("acquire readout async = " + str(self._asyncReadout))
        try:
            n = rows * cols * 2
            if self._asyncReadout:
                raw_data = self.readout_async(n)
                self._set_state(XCamConst.STATE_DATA_READY)
            else:
                cmdline = XCamConst.READOUT_EXE.format(n)
                # cmdline = "%s xcam.py -e readout -n %d" % (sys.executable, n)
                res = os.system(cmdline)
                log.info("os.system(%s) res = %d" % (cmdline, res))
                if not os.path.exists(XCamConst.DATA_FILE):
                    log.warning("%s not found. Waiting 2 seconds ..." % XCamConst.DATA_FILE)
                    # print "WARNING: %s not found. Waiting 2 seconds ..." % (DATA_FILE)
                    time.sleep(2.0)
                if not os.path.exists(XCamConst.DATA_FILE):
                    log.error("%s not found." % XCamConst.DATA_FILE)
                raw_data = numpy.fromfile(XCamConst.DATA_FILE, dtype='uint16')
                self._set_state(XCamConst.STATE_DATA_READY)

        except XCamException as ex:
            self._set_state(XCamConst.STATE_ERROR)
            raise ex

        finally:
            pass

        if self.get_header('remove_top_half', False):
            print("removing top half of image mode")
            self.set_param(Param.addr_rows, rows//2)

        self._set_state(XCamConst.STATE_IDLE)

        if self._bits == 14:
            raw_data = raw_data & 0x3fff

        return raw_data

    def clock_out_memory_location(self, loc):

        if self.get_sync_state():
            self.set_param(Param.addr_dump_memory, -1)

        self.set_param(Param.addr_dump_memory, loc)

        def sanity_counter(bit_i, trig_state, msg):
            if bit_i == -1:
                sanity_count = 1000
            else:
                sanity_count = 20

            pause_time = 0.001
            # time.sleep(pauseTime)
            i = 0
            while self.get_sync_state() == trig_state:
                time.sleep(pause_time)
                sanity_count -= 1
                i += 1
                if sanity_count == 0:
                    raise RuntimeWarning("bit %d %s" % (bit_i, msg))
            # print i

        val = 0
        try:
            sanity_counter(-1, False, "sanity counter 1 signalled failure")
            for bit in range(0, 16):
                # print _i, "clock_out_memory_location"
                self.handshake(True)
                sanity_counter(bit, False, "sanity counter 2 signalled failure")

                s = self.get_led_state()
                val <<= 1
                val += int(s)

                self.handshake(False)
                sanity_counter(bit, True, "sanity counter 3 signalled failure")
        except RuntimeWarning as ex:
            print(str(ex))
            return None
        # t1 = time.time()
        # print "%04x" % loc, "%04x" % val, "%0.3f" % (t1-t0)

        return val

    @staticmethod
    def has_io_port():
        return XCamConst.HAS_IO_PORT

    def get_led_state(self):
        """
        Input.
        Pin 13 of the PC parallel port "listens" to the pin 12 (SIGNAL_1_SYNC)
        of the XCam rack's 15 pin port.
        """
        if XCamConst.HAS_IO_PORT:
            self._mutex.acquire()
            try:
                s = parport.Inp32(0x379)
                v = (s & (1 << 4)) > 0  # pin 13 S4 of (S0-S7)
                return v
            finally:
                self._mutex.release()
        else:
            if XCamConst.IS_SIMULATING:
                return self.__state == XCamConst.STATE_INTEGRATING
            else:
                return False

    def get_sync_state(self):
        """
        Input.
        Pin 12 of the PC parallel port "listens" to the pin 4 (SIGNAL_1_SYNC)
        of the XCam rack's 15 pin port.
        """
        if XCamConst.HAS_IO_PORT:
            self._mutex.acquire()
            try:
                s = parport.Inp32(0x379)
                v = (s & (1 << 5)) > 0  # pin 12 S5 of (S0-S7)
                return v
            finally:
                self._mutex.release()
        else:
            # print "xcam.get_sync_state is being simulated"
            return False

    def get_shutter_state(self):
        return self._shutState

    def is_shutter_enabled(self):
        return self._controlInternalShutter

    def set_shutter_enabled(self, to_set):
        self._controlInternalShutter = to_set

    def shutter(self, state):
        """
        Output.
        Pin 3 (D1) on the PC parallel port is connected to the box that
        controls the internal shutter.
        """
        if XCamConst.HAS_IO_PORT:
            self._shutState = state
            self._mutex.acquire()
            try:
                v = parport.Inp32(0x378)
                bit = 1
                if state:
                    v |= (1 << bit)
                else:
                    v &= ~(1 << bit)
                parport.Out32(0x378, v)
            finally:
                self._mutex.release()

    def handshake(self, state=1):
        """
        Input.
        Pin 2 (D0) on the PC parallel port is connected to pin 3 (PF6_INPUT)
        of the XCam rack's 15 pin port.
        """
        if XCamConst.HAS_IO_PORT and XCamConst.USE_HANDSHAKING:
            self._mutex.acquire()
            try:
                v = parport.Inp32(0x378)
                bit = 0
                if state:
                    v |= (1 << bit)
                else:
                    v &= ~(1 << bit)
                parport.Out32(0x378, v)
            finally:
                self._mutex.release()

    def readout_async(self, byte_count):
        dev = self._com
        total = byte_count
        bufs = []
        trans_ids = []
        while byte_count > 0:
            if byte_count < XCamConst.MAX_CHUNKSIZE:
                n = byte_count
            else:
                n = XCamConst.MAX_CHUNKSIZE

            bufs.append(QuickUsb.CreateByteBuffer(n))
            byte_count -= n

        byte_count = total
        for buf in bufs:
            n = len(buf)
            (ok, transId) = dev.ReadDataAsync(buf, n)
            if not ok:
                ex = QuickUSBException(dev)
                self.cancel_readout()
                raise ex
            else:
                print("trans-id=", transId, " buf len=", n)
                trans_ids.append(transId)

        # TODO: place a time.sleep() loop here
        # time.sleep(10.0)

        self.handshake(1)
        for transId in trans_ids:
            t0 = time.time()
            (ok, n) = dev.AsyncWait(transId, 0)
            t1 = time.time()
            if not ok:
                ex = QuickUSBException(dev)
                self.handshake(0)
                self.cancel_readout()
                raise ex
            else:
                byte_count -= n
                print("%0.3f transid %d read %d bytes, N=%d, in=%d"
                      % (t1-t0, transId, n, byte_count, (total-byte_count)))
        self.handshake(0)

        raw_data = numpy.array([], dtype='uint16')
        for buf in bufs:
            raw_data = numpy.append(raw_data, numpy.frombuffer(buf, dtype='uint16'))

        print("finished N=%d" % byte_count)

        if byte_count != 0:
            raise XCamException("Failed to readout all data. %d bytes left to read" % byte_count, -1)

        return raw_data

    def readout(self, byte_count):

        dev = self._com
        total = byte_count
        bufs = []
        while byte_count > 0:
            if byte_count < XCamConst.MAX_CHUNKSIZE:
                n = byte_count
            else:
                n = XCamConst.MAX_CHUNKSIZE

            bufs.append(QuickUsb.CreateByteBuffer(n))
            byte_count -= n

        t0 = time.time()
        byte_count = total
        self.handshake(1)
        for buf in bufs:
            n = len(buf)
            print("reading %d bytes" % n)
            (ok, _read) = dev.ReadData(buf, n)
            if not ok:
                self.handshake(0)
                ex = QuickUSBException(dev)
                self.cancel_readout()
                raise ex

            t1 = time.time()
            print("%0.3f read %d bytes, N=%d, in=%d" % (t1-t0, n, byte_count, (total-byte_count)))
            t0 = t1
            byte_count -= n
        self.handshake(0)

        raw_data = numpy.array([], dtype='uint16')
        for buf in bufs:
            raw_data = numpy.append(raw_data, numpy.frombuffer(buf, dtype='uint16'))

        print("finished N=%d" % byte_count)

        if byte_count != 0:
            raise XCamException("Failed to readout all data. %d bytes left to read" % byte_count, -1)

        return raw_data

    def set_usb_timeout(self, timeout_in_ms):
        """ Set the USB response timeout in milli-seconds"""
        dev = self._com
        (ok,) = dev.SetTimeout(timeout_in_ms)
        logging.getLogger("xcam").info("set_usb_timeout(%d)" % timeout_in_ms)
        if not ok:
            if platform.architecture()[0] == '32bit':
                raise QuickUSBException(dev)
            else:
                # TODO: 64bit quick usb issue with SetTimeout
                pass  # 64bit driver always returns an error

    def identify(self):
        """
        Retrieve the interface identifier. Example::

            "Bitwise Systems; QuickUSB QUSB2 Module v2.11rc7 (FIFO Handshake); 4633"
        """
        dev = self._com
        (_ok, make) = dev.Make
        (_ok, model) = dev.Model
        (_ok, serial) = dev.Serial

        return make + "; " + model + "; " + serial

    def version(self):
        """ return the XCAM version information from the device. """
        dev = self._com
        self.reset_fifo()
        self.write(XCamConst.CMD_VERSION)
        buf = QuickUsb.CreateByteBuffer(12)
        (ok, _read) = dev.ReadData(buf, len(buf))
        if not ok:
            raise QuickUSBException(dev, "XCam version read data error. ")

        return ''.join([chr(x) for x in buf[2:]])

    def load_rack(self):
        # self.load_rack_state(cmds=[CMD_BIAS_VOLTAGE, CMD_CLOCK_VOLTAGE])
        self.write(self._dsp.bytes)
        # self.load_rack_state()

    def load_rack_state(self, cmds=None):
        """
        This reinitializes the XCAM rack with all the settings from the
        previously run session. The parameters that are set are::

            * bias voltages
            * clock voltages
            * gain
            * delays
            * CCD power on (or off)

        The XCAM rack does not enable getter commands, thus it is impossible
        to know what the last known state of the rack is. To address this
        problem, all QuickUSB commands that update the rack state are saved
        to the xcam_state.txt file. This file is read in when a new instance
        of the XCam class is instantiated.

        *arguments*
            `cmds` : optional list or tuple. Enables only certain specied
                commands to be sent, example::
                    cmds=[CMD_BIAS_VOLTAGE, CMD_CLOCK_VOLTAGE]
        """
        log = logging.getLogger("xcam")
        log.info("Loading last known XCam rack state...")
        keys = sorted(self._rack.commands.keys(), key=lambda x: (x,) if isinstance(x, int) else x)

        for key in keys:
            if cmds is not None:
                cmd = key
                if isinstance(key, tuple):
                    cmd = key[0]
                if cmd not in cmds:
                    continue

            val = self._rack.commands[key]
            # time.sleep(1.0)
            # print "key=", key, type(key), "val=", val, type(val)
            self.write(key, val)

        self._set_state(XCamConst.STATE_IDLE)

    def save_volts(self, fpath=None):
        """
        Save the voltage configuration parameters to XCam formatted file
        """
        self._voltages.save(fpath)

    def load_volts(self, fpath=None):
        """
        Loads the voltage configuration file and sets the rack voltages
        accordingly.
        """
        if fpath:
            self._voltages = VoltageFile(fpath)
        for adu in self._voltages:
            self.set_voltage(adu.command, adu.address, int(adu))

    def save_params(self, fpath):
        """
        Save the voltage configuration parameters to XCam formatted file
        """
        pass

    def load_params(self, fpath):
        """
        Loads the delay parameters from a file and uploads the settings to the
        ADSP2181 chip on the rack.
        """
        with open(fpath) as file_obj:
            i = 0
            for line in file_obj:
                try:
                    adu = int(line.strip())
                    self.set_param(i, adu)
                except ValueError:
                    pass
                i += 1

    def load_seq(self, seq_path=None):
        """
        Uploads the DSP sequencer file to the ADSP2181 chip on the rack.
        """
        if seq_path:
            self._dsp = DSPFile(seq_path)
        self.write(self._dsp.bytes)

    def set_gain(self, val):
        """
        Set the XCam gain to one of the 4 gain settings.
        3 (D) is highest gain, 0(A) is the lowest gain.

        Protocol::
            0x0c, [val]

        @param val: 0=A,1=B,2=C,3=D. Both str and int types are accepted, i.e.
            "A" is converted to 0, and so are equivalent.

        """
        if isinstance(val, str):
            if 'A' <= val <= 'D':
                val = ord(val) - ord('A')
            else:
                val = int(val)
        self.write(XCamConst.CMD_GAIN, val)

    def set_power(self, val):
        """ Set the CCD power on (1) or off (0) """
        self.write(XCamConst.CMD_POWER, int(val))

    def set_voltage(self, cmd, addr, val):
        """ The voltage adu settings is limited to a range between 0 and 255 """
        if self.is_busy(True, cmd):
            return

        adu = self._voltages.find(cmd, addr)
        if type(val) == float:
            if val < 0.0:
                log = logging.getLogger("xcam")
                s = "%s %0.2f V setting is out of bounds. Setting to 0.0V" % (adu.label, val)
                log.warning(s)
                val = 0.0

            # print adu.key, self._voltageRangeChecks
            if adu.key in self._voltageRangeChecks:
                minval, maxval = self._voltageRangeChecks[adu.key]
                if val < minval or val > maxval:
                    rng = (minval, maxval)
                    raise VoltageOutOfRangeException(adu.key, val, rng)

            adu.set_value(val)
        else:
            if val < 0:
                log = logging.getLogger("xcam")
                s = "%s %d ADU V setting is out of bounds. Setting to 0 ADUV" % (adu.label, val)
                log.warning(s)
                val = 0

            if adu.key in self._voltageRangeChecks:
                volt = adu.adu2volt(val)
                min_val, max_val = self._voltageRangeChecks[adu.key]
                if volt < min_val or volt > max_val:
                    rng = (min_val, max_val)
                    raise VoltageOutOfRangeException(adu.key, volt, rng)

            adu.set_adu(val)

        self.write(cmd, [addr, int(adu) & 0xff, 0x00])

    def set_voltage_clock(self, addr, adu):
        """ Set a clock voltage. """
        self.set_voltage(XCamConst.CMD_CLOCK_VOLTAGE, addr, adu)

    def set_voltage_bias(self, addr, adu):
        """ Set a bias voltage. """
        self.set_voltage(XCamConst.CMD_BIAS_VOLTAGE, addr, adu)

    def get_voltage(self, cmd, addr):
        return self._voltages.find(cmd, addr)

    def get_voltage_clock(self, addr):
        return self.get_voltage(XCamConst.CMD_CLOCK_VOLTAGE, addr)

    def get_voltage_bias(self, addr):
        return self.get_voltage(XCamConst.CMD_BIAS_VOLTAGE, addr)

    def set_param(self, addr, adu):
        """
        Set a XCAM DSP parameter to a new value.

        Protocol::

            0x0b, [addr], [adu:lsb], [adu:msb]

        @note: this is the same as the set_delay method and protocol.
        @see: set_clocking, set_delay

        @param addr: 0 to 72 address parameters as described in the DSP header.
        @param adu: 0 to 16383 14bit value that the DSP parameter address
            is to be set at.
        """
        rng = Param.get_range(addr)

        try:
            adu = int(adu)
        except ValueError:
            raise ParamRangeException(addr, adu, rng)

        if addr == Param.addr_trappump_cycles or addr == Param.addr_ser_trappump_cycles:
            adu //= 10  # multiplying factor of 10 added to DSP code 02/09/2014

        if rng:
            if adu not in rng:
                raise ParamRangeException(addr, adu, rng)

        self.write(XCamConst.CMD_PARAM, [addr, adu & 0xff, (adu >> 8) & 0xff])

    def clear_charge(self, pause1 = 5.0, pause2=15.0):
        """
        Clears the residual surface charge. This should be done when the
        CCD power has undergone a power cycle.
        """
        log = logging.getLogger("xcam")
        if self.state != XCamConst.STATE_IDLE:
            log.info("Busy. Ignoring clear charge call.")
            return

        self._set_state(XCamConst.STATE_CLEARING_CHARGE)
        log.info("clearing residual surface charge")
        adu = self._voltages.find_by_key('vbias_6_ss')
        adu.set_value(9.0)
        self.set_voltage_bias(adu.address, int(adu))
        log.info("waiting %d seconds..." % int(pause1))
        self._timeClear = time.time()
        time.sleep(pause1)

        adu.set_value(0.0)
        self.set_voltage_bias(adu.address, int(adu))
        log.info("waiting %d seconds..." % int(pause2))
        time.sleep(pause2)
        log.info("finished clearing residual charge")
        self._set_state(XCamConst.STATE_IDLE)


class Readout(object):

    @staticmethod
    def byte2short(vals):
        lsb = vals[0]
        msb = vals[1]
        val = (msb << 8) | lsb
        return val

    # @staticmethod
    # def short2byte(val):
    #     lsb = 0xff & val
    #     msb = 0xff & (val >> 8)
    #     return lsb, msb

    @staticmethod
    def readout(byte_count=None):
        cam = XCam()
        cam.set_usb_timeout(300 * 1000)
        if byte_count is None:
            cols = Readout.byte2short(cam.rack.get_param(Param.addr_cols))
            rows = Readout.byte2short(cam.rack.get_param(Param.addr_rows))
            rdir = Readout.byte2short(cam.rack.get_param(Param.addr_readout_dir))
            chns = Readout.byte2short(cam.rack.get_param(Param.addr_channels))
            if chns == 4:
                if (rdir == 2) or (rdir == 3):
                    cols *= 2
            byte_count = cols * rows * 2

        try:
            # remove the temporary data file
            os.remove(XCamConst.DATA_FILE)
        except OSError:
            pass

        raw_data = cam.readout(byte_count)
        if XCamConst.IS_SIMULATING:
            raw_data *= numpy.random.rand(*raw_data.shape)
        # if all the data is retrieved, then save the raw data to the temporary
        # data file so the calling application can extract it.
        raw_data.tofile(XCamConst.DATA_FILE)
        cam.close()
        return raw_data

    @staticmethod
    def decode(data, rows, cols, channels, node_location="1234", node_orientation="NHBV", rdir=1):
        """ de-multiplexes the raw data.
            Returns unsigned 16 bit rows x cols numpy array.
        """
        if isinstance(channels, str):
            channel_map = {
                "16Q": 4,
                "16D": 2,
                "16S": 1,
                "14Q": 4,
                "14D": 2,
                "14S": 1,
            }
            channels = channel_map[channels]

        print("Decode %d channels" % channels)
        if channels == 4:
            if (rdir == 2) or (rdir == 3):
                cols *= 2

            print(cols, rows, len(data), data.shape, rdir)
            r, c, r2, c2 = rows, cols, rows//2, cols//2

            # TODO: temporary!!!!
            # return numpy.array(data).astype(numpy.uint16).reshape(r, c)

            remove_top_half = False
            try:
                data = data.reshape(r * c)  # it must be a 1D array to work!!
            except ValueError:
                r *= 2
                r2 = r//2
                data = data.reshape(r * c)
                remove_top_half = True

            # make sure that the decoding parameters are initialized
            # (if they are not)
            if not node_location:
                node_location = "1234"
            if not node_orientation:
                node_orientation = "NHBV"

            # print nodeLocation, nodeOrientation, type(nodeLocation), type(nodeOrientation)

            # check that the decoding parameters are valid formats
            if not re.search(r'[NHBV]{4}', node_orientation):
                print("ERROR: Decode nodeOrientation contains invalid character", node_orientation)
                node_orientation = "NHBV"

            if len(set(node_orientation)) != len(node_orientation):
                print("ERROR: Decode nodeOrientation contains duplicate character", node_orientation)
                node_orientation = "NHBV"

            if not re.search(r'[1234]{4}', node_location):
                print("ERROR: Decode nodeLocation contains invalid character", node_location)
                node_location = "1234"

            if len(set(node_location)) != len(node_location):
                print("ERROR: Decode nodeLocation contains duplicate character", node_location)
                node_location = "1234"

            # nodeLocation    = "1234"
            # nodeOrientation = "NHBV"
            # nodeOrientation = ".-|+"

            out = numpy.zeros((r, c), dtype='uint16')
            for i in range(4):
                loc = int(node_location[i])
                idx = loc - 1
                node = data[idx::4].reshape((r2, c2))
                if node_orientation[i] == 'V':
                    node = numpy.flipud(node)
                elif node_orientation[i] == 'H':
                    node = numpy.fliplr(node)
                elif node_orientation[i] == 'B':
                    node = numpy.fliplr(node)
                    node = numpy.flipud(node)

                if i == 0:
                    out[0:r2, 0:c2] = node  # top left
                elif i == 1:
                    out[0:r2, c2:c] = node  # top right
                elif i == 2:
                    out[r2:r, c2:c] = node  # bottom right
                elif i == 3:
                    out[r2:r, 0:c2] = node  # bottom left

            if rdir == 2:
                out = out[0:r, c2:c]

            if rdir == 3:
                out = out[0:r, 0:c2]

            if remove_top_half:
                out = out[:r//2, :]

        elif channels == 2:
            if (rdir == 2) or (rdir == 3):
                r = rows
                r2 = r // 2
                c = cols
                out = numpy.zeros((r, c), dtype='uint16')
                data = data.reshape(r * c)  # it must be a 1D array to work!!
                # i = 0
                # N = r
                ch0 = data[0::2]
                ch0 = ch0.reshape((r2, c))
                ch0 = numpy.flipud(ch0)
                if rdir == 2:
                    ch0 = numpy.fliplr(ch0)

                ch1 = data[1::2]
                ch1 = ch1.reshape((r2, c))
                if rdir == 2:
                    ch1 = numpy.fliplr(ch1)

                out[r2: r, 0:c] = ch0
                out[0: r2, 0:c] = ch1

            if (rdir == 0) or (rdir == 1):
                r = rows
                c = cols
                out = numpy.zeros((r, c), dtype='uint16')
                data = data.reshape((r, c))
                # data = data & 0x3fff
                i = 0
                N = r
                for line in data:
                    line = numpy.append(line[1::2], line[0::2][::-1])
                    out[N-i-1] = line
                    i += 1
        else:
            # the 1 channel CCD only has 15 bits
            out = data ^ 0x8000
            print("rows, cols=", rows, cols, "data.shape=", data.shape, out.dtype)
            out = out.astype('uint16').reshape((rows, cols))

        return out

    @staticmethod
    def save_data(fname, data, header=None):

        if os.path.exists(fname):
            os.remove(fname)

        is_fits_file = os.path.splitext(fname)[1].lower() in [".fits", ".fit"]
        if is_fits_file:
            from astropy.io import fits as pyfits

            fits = pyfits.PrimaryHDU(data)
            if header:
                for entry in header:
                    try:
                        fits.header.update(entry.key, entry.value, entry.desc)
                    except ValueError as e:
                        s = "Failed to write fits header entry: "
                        s += entry.key + "=" + str(entry.value) + ";" + str(e)
                        print(s)

            fits.writeto(fname)

        else:
            data.tofile(fname)


parport = ParallelPortSimulator
if XCamConst.USE_HANDSHAKING:
    try:
        if platform.architecture()[0] == '32bit':
            print("Loading inpoutx64")
            parport = ctypes.windll.inpoutx64
        else:
            print("Loading inpoutx64")
            parport = ctypes.windll.inpoutx64
    except:
        XCamConst.HAS_IO_PORT = False
        XCamConst.USE_HANDSHAKING = False


def set_simulation_mode(is_sim):
    if is_sim:
        XCamConst.DRIVER = Simulator
        XCamConst.IS_SIMULATING = True
    else:
        XCamConst.DRIVER = QuickUsb
        XCamConst.IS_SIMULATING = False

        dev_err = 0
        dev = QuickUsb.QuickUsb()
        (ok, _names) = dev.FindModules()
        if not ok:
            dev_err = dev.GetLastError()
        dev.Close()

        if dev_err != 0:
            print("xcam driver configuration error: ", str(QuickUsb.Error(dev_err)))
            print("forcing using xcam simulator to be used instead.")
            XCamConst.DRIVER = Simulator
            XCamConst.IS_SIMULATING = True

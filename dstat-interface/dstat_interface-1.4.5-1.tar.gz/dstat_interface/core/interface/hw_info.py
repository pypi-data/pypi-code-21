#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from ..dstat import state, dfu
from ..dstat.comm import dstat_logger, exp_logger

import logging
import time
import serial

logger = logging.getLogger(__name__)

try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, GObject
except ImportError:
    print("ERR: GTK not available")
    sys.exit(1)

class InfoDialog(object):
    def __init__(self, parent, connect, signal='activate'):
        self.parent = parent
        connect.connect(signal, self.activate)

    def activate(self, object=None, data=None):
        self.dialog = Gtk.MessageDialog(self.parent, 0, Gtk.MessageType.INFO,
                                        Gtk.ButtonsType.OK, "DStat Info")
        self.dialog.format_secondary_text(
            "PCB Version: {}\n".format(state.dstat_version.base_version) + 
            "Firmware Version: {}".format(state.firmware_version)
        )
        
        self.dialog.connect('response', self.destroy)
        self.dialog.show()
        
    def destroy(self, object=None, data=None):
        self.dialog.destroy()


class ResetDialog(object):
    def __init__(self, parent, connect, stop_callback, disconnect_callback, signal='activate'):
        self.parent = parent
        self.stop = stop_callback
        self.disconnect = disconnect_callback
        connect.connect(signal, self.activate)

    def activate(self, object=None, data=None):
        dialog = Gtk.MessageDialog(self.parent, 0, Gtk.MessageType.WARNING,
                                        Gtk.ButtonsType.OK_CANCEL, "EEPROM Reset")
        dialog.format_secondary_text("This will reset the DStat's EEPROM settings, then disconneect."
        )

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.dstat_reset_eeprom()
        dialog.destroy()

    def dstat_reset_eeprom(self):
        """Tries to contact DStat and resets EEPROM.
        If no response, returns False, otherwise True.
        """
        self.stop()
        exp = EEPROMReset()
        state.ser.start_exp(exp)
        logger.info("Resetting DStat EEPROM…")
        while True:
            result = state.ser.get_proc(block=True)
            if result in ('SERIAL_ERROR', 'DONE', 'ABORT'):
                break
        logger.info(result)

        self.disconnect()


class EEPROMReset(object):
    def __init__(self):
        pass

    def run(self, ser, ctrl_pipe, data_pipe):
        status = None
        try:
            ser.write(b'!2\n')
            exp_logger.info('!2')

            for i in range(10):
                if ser.readline().rstrip() == b"@ACK 2":
                    dstat_logger.info('@ACK 2')
                    ser.write(b'SD\n')
                    exp_logger.info('SD')
                    status = "DONE"
                    time.sleep(5)
                    break
                else:
                    time.sleep(.5)
                    ser.reset_input_buffer()
                    ser.write(b'!2\n')
                    exp_logger.info('!2')
                    time.sleep(.1)

        except UnboundLocalError as e:
            status = "SERIAL_ERROR"
        except serial.SerialException as e:
            logger.error('SerialException: %s', e)
            status = "SERIAL_ERROR"
        finally:
            return status
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#     DStat Interface - An interface for the open hardware DStat potentiostat
#     Copyright (C) 2014  Michael D. M. Dryden -
#     Wheeler Microfluidics Laboratory <http://microfluidics.utoronto.ca>
#
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import subprocess
import sys
import os
import time
import logging
from tempfile import mkdtemp
from zipfile import ZipFile

if sys.version_info >= (3,):
    import urllib.request as urllib2
    import urllib.parse as urlparse
else:
    import urllib2
    import urlparse

logger = logging.getLogger(__name__)

try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk
except ImportError:
    print("ERR: GTK not available")
    sys.exit(1)

import serial

from . import state
from .comm import dstat_logger, exp_logger

fwurl = "http://microfluidics.utoronto.ca/gitlab/api/v4/projects/4/jobs/artifacts/master/download?job=1.2.3&private_token=zkgSx1FaaTP7yLyFKkX6"

class FWDialog(object):
    def __init__(self, parent, connect, stop_callback, disconnect_callback, signal='activate'):
        self.parent = parent
        self.stop = stop_callback
        self.disconnect = disconnect_callback
        connect.connect(signal, self.activate)
    
    def activate(self, widget=None, data=None):
        for name, result in assert_deps().items():
            if result is not True:
                logger.error("Can't use firmware update module.")
                self.missing_deps()
                return
                
        self.stop() # Stop OCP
        version_result, master = test_firmware_version() 
        
        if version_result is False:
            self.git_error()
            return
        
        if version_result == 'latest':
            message = "Your firmware is already up to date."
            secondary = "Click yes to reflash firmware anyways."
        elif version_result == 'devel':
            message = "Your firmware is not on the master branch."
            secondary = "You may have a development version. " +\
                        "Click yes to reflash firmware anyways."
        elif version_result == 'old':
            message = "Your firmware is out of date."
            secondary = "Click yes to flash the latest firmware."
        
        dialog = Gtk.MessageDialog(self.parent, 0, Gtk.MessageType.INFO,
                                   Gtk.ButtonsType.YES_NO, message)
        dialog.format_secondary_text(secondary)
        dialog.get_content_area().add(
            Gtk.Label(
                label="Installed version: {}".format(state.firmware_version)))
                
        dialog.get_content_area().add(
            Gtk.Label(label="Latest version: {}".format(master)))
                
        dialog.show_all()
        response = dialog.run()
        
        if response == Gtk.ResponseType.YES:
            try:
                download_fw()
            except:
                self.dl_error()
                return
            
            dstat_enter_dfu()
            
            self.dfu_notice()
            self.disconnect()
            try:
                dfu_program()
            except:
                self.dfu_error()
                
            dialog.destroy()
            
        else:
            dialog.destroy()
    
    def missing_deps(self):
        dialog = Gtk.MessageDialog(
                     self.parent, 0, Gtk.MessageType.ERROR,
                     Gtk.ButtonsType.OK, "Missing Dependencies")
        
        dialog.format_secondary_text('Check console for more info.')
        
        dialog.connect('response', self.destroy)
        dialog.show()
    
    def git_error(self):
        dialog = Gtk.MessageDialog(
                     self.parent, 0, Gtk.MessageType.ERROR,
                     Gtk.ButtonsType.OK, "Git Error")
        
        dialog.format_secondary_text('Check console for more info.')
        
        dialog.connect('response', self.destroy)
        dialog.show()
        
    def dl_error(self):
        dialog = Gtk.MessageDialog(
                     self.parent, 0, Gtk.MessageType.ERROR,
                     Gtk.ButtonsType.OK, "Download Error")
        
        dialog.format_secondary_text('Check console for more info.')
        
        dialog.connect('response', self.destroy)
        dialog.show()
    
    def dfu_notice(self):
        dialog = Gtk.MessageDialog(
                     self.parent, 0, Gtk.MessageType.INFO,
                     Gtk.ButtonsType.OK, "Note about DFU")
        
        dialog.format_secondary_text("Click OK once the DStat has connected in "
            + "DFU mode. Windows doesn't seem to like the automatic reboot. " 
            + "Try holding down the reset button while plugging the "
            + 'USB port in (No LEDs should be lit), then click OK. Make sure '
            + 'the DFU driver from the dfu-programmer directory is installed.')
        
        dialog.run()
        dialog.destroy()
        
    def dfu_error(self):
        dialog = Gtk.MessageDialog(
                     self.parent, 0, Gtk.MessageType.ERROR,
                     Gtk.ButtonsType.OK, "Could not update over DFU")
        
        dialog.format_secondary_text('Check console for more info.')
        
        dialog.connect('response', self.destroy)
        dialog.show()
        
    def destroy(self, widget=None, data=None):
        widget.destroy()
    

def assert_deps():
    deps = {'git' : 'git --version',
            'dfu-programmer' : 'dfu-programmer --version'}
    
    result = {}
    
    for key, command in deps.items():        
        try:
            output = subprocess.check_output(command.split(),
                                             stderr=subprocess.STDOUT)
            logger.info("%s\n%s", command, output)
            result[key] = True
        except subprocess.CalledProcessError:
            logger.warning("{} is not available.".format(key))
            result[key] = False
            
    return result

def download_fw():  # from https://stackoverflow.com/a/16518224
    temp_dir = mkdtemp()
    logger.info("Temporary directory: {}".format(temp_dir))
    os.chdir(temp_dir)  # Go to temporary directory
    
    u = urllib2.urlopen(fwurl)

    scheme, netloc, path, query, fragment = urlparse.urlsplit(fwurl)
    filename = os.path.basename(path)
    if not filename:
        filename = 'downloaded.file'

    with open(filename, 'wb') as f:
        meta = u.info()
        meta_func = meta.getheaders if hasattr(meta, 'getheaders') else meta.get_all
        meta_length = meta_func("Content-Length")
        file_size = None
        if meta_length:
            file_size = int(meta_length[0])
        logger.info("Downloading: {0} Bytes: {1}".format(fwurl, file_size))

        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break

            file_size_dl += len(buffer)
            f.write(buffer)

            status = "{0:16}".format(file_size_dl)
            if file_size:
                status += "   [{0:6.2f}%]".format(file_size_dl * 100 / file_size)
            status += chr(13)
            logger.info(status)
    
    with ZipFile(filename, mode='r') as z:
        fw_path = z.extract('dstat-firmware.hex')
    
    return fw_path

def test_firmware_version(current=None):
    if current is None:
        current = state.firmware_version
    
    temp_dir = mkdtemp()
    logger.info("Temporary directory: {}".format(temp_dir))
    os.chdir(temp_dir)  # Go to temporary directory
    
    command = "git clone http://microfluidics.utoronto.ca/gitlab/dstat/dstat-firmware.git"
    logger.info('Cloning master.')
    try:
        output = subprocess.check_output(command.split(),
                                         stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        logger.error("git failed with error code {}".format(e.returncode))
        logger.error("Output: {}".format(e.output))
        return False, None
    logger.info(output)
    
    os.chdir("./dstat-firmware")
    
    command = "git rev-parse --short master"
    master = subprocess.check_output(command.split(), stderr=subprocess.STDOUT)
    logger.info("Current master commit: {}".format(master))
    
    command = "git merge-base --is-ancestor master {}".format(current)
    test = subprocess.call(command.split())
    
    if test == 0:  # already newest
        logger.info('Firmware is latest available.')
        return 'latest', master
    elif test == 1:  # old version
        logger.info('Firmware is out of date.')
        return 'old', master
    elif test == 128:  # newer or different branch
        logger.info('Firmware is not on the master branch.')
        return 'devel', master
    else:
        logger.error('Unexpected git error. Git exited {}'.format(test))
        return False, None

def dfu_program(path='./dstat-firmware.hex'):
    """Tries to program DStat over USB with DFU with hex file at path."""
    try:
        command = "dfu-programmer atxmega256a3u erase"
        output = subprocess.check_output(command.split(),
                                          stderr=subprocess.STDOUT)
        logger.info("%s\n%s", command, output)
        command = "dfu-programmer atxmega256a3u flash {}".format(path)
        output = subprocess.check_output(command.split(),
                                          stderr=subprocess.STDOUT)
        logger.info("%s\n%s", command, output)
        command = "dfu-programmer atxmega256a3u launch"
        output = subprocess.check_output(command.split(),
                                          stderr=subprocess.STDOUT)
        logger.info("%s\n%s", command, output)
    except subprocess.CalledProcessError as e:
        logger.error("{} failed with output:".format(" ".join(e.cmd)))
        logger.error(e.output)
        raise


def dstat_enter_dfu():
    """Tries to contact DStat and get version. Stores version in state.
    If no response, returns False, otherwise True.
        
    Arguments:
    ser_port -- address of serial port to use
    """
    exp = DFUMode()
    state.ser.start_exp(exp)
    while True:
        result = state.ser.get_proc(block=True)
        if result in ('SERIAL_ERROR', 'DONE'):
            break
    logger.info(result)
    # state.ser.disconnect()

    time.sleep(.1)
    
    return True


class DFUMode(object):
    def __init__(self):
        pass
        
    def run(self, ser, ctrl_pipe, data_pipe):
        """Tries to contact DStat and get version. Returns a tuple of
        (major, minor). If no response, returns empty tuple.
            
        Arguments:
        ser_port -- address of serial port to use
        """
        status = None
        try:
            ser.write(b'!2\n')
            exp_logger.info('!2')
    
            for i in range(10):
                if ser.readline().rstrip() == b"@ACK 2":
                    dstat_logger.info('@ACK 2')
                    ser.write(b'SF\n')
                    exp_logger.info('SF')
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


if __name__ == "__main__":
    log_handler = logging.StreamHandler()
    log_formatter = logging.Formatter(
                        fmt='%(asctime)s %(levelname)s: [%(name)s] %(message)s',
                        datefmt='%H:%M:%S'
                    )
    log_handler.setFormatter(log_formatter)
    logger.setLevel(level=logging.INFO)
    logger.addHandler(log_handler)
        
    dstat_enter_dfu()
    time.sleep(2)
    dfu_program(sys.argv[1])
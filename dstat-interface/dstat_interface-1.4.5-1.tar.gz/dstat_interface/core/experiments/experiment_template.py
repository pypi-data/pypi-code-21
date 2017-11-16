#!/usr/bin/env python
# -*- coding: utf-8 -*-
#     DStat Interface - An interface for the open hardware DStat potentiostat
#     Copyright (C) 2017  Michael D. M. Dryden - 
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
import logging
import struct
from datetime import datetime
from collections import OrderedDict
from copy import deepcopy
from math import ceil
import time

from pkg_resources import parse_version

try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, GObject
except ImportError:
    print "ERR: GTK not available"
    sys.exit(1)


from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt

from matplotlib.backends.backend_gtk3agg \
    import FigureCanvasGTK3Agg as FigureCanvas
 
from pandas import DataFrame
import seaborn as sns
sns.set(context='paper', style='darkgrid')

import serial

from ..errors import InputError, VarError
from ..dstat import state, comm
from ..dstat.comm import TransmitError

logger = logging.getLogger(__name__)
dstat_logger = logging.getLogger("{}.DSTAT".format(comm.__name__))
exp_logger = logging.getLogger("{}.Experiment".format(__name__))

class Experiment(object):
    """Store and acquire a potentiostat experiment. Meant to be subclassed
    to by different experiment types and not used instanced directly. Subclass
    must instantiate self.plotbox as the PlotBox class to use and define id as
    a class attribute.
    """
    id = None
    
    def __init__(self, parameters):
        """Adds commands for gain and ADC."""
        self.parameters = parameters
        self.databytes = 8
        self.datapoint = 0
        self.scan = 0
        self.time = 0
        self.plots = []
        
        self.re_voltage_scale = state.board_instance.re_voltage_scale

        self.gain = state.board_instance.gain[int(self.parameters['gain'])]

        try:
            self.gain_trim = int(
                state.settings[
                    state.board_instance.gain_trim[int(self.parameters['gain'])]
                ][1]
            )
        except AttributeError:
            logger.debug("No gain trim table.")

        self.commands = ["EA", "EG"]
        
        if self.parameters['buffer_true']:            
            self.commands[0] += "2"
        else:
            self.commands[0] += "0"
        self.commands[0] += " {p[adc_rate]} {p[adc_pga]} ".format(
            p=self.parameters)
        self.commands[1] += "{p[gain]} {p[short_true]:d} ".format(
            p=self.parameters)
        
        self.setup()
        self.time = [datetime.utcnow()]
              
    def setup(self):
        self.data = OrderedDict(current_voltage=[([], [])])
        
        self.columns = ['Voltage (mV)', 'Current (A)']
        self.plot_format = {
                            'current_voltage' : {'labels' : self.columns,
                                                 'xlims' : (0, 1)
                                                 }
                            }
        # list of scans, tuple of dimensions, list of data
        self.line_data = ([], [])
        
        self.plots.append(PlotBox(['current_voltage']))
        
    def write_command(self, cmd, params=None, retry=5):
        """Write command to serial with optional number of retries."""
        def get_reply(retries = 3):
            while True:
                reply = self.serial.readline().rstrip()
                if reply.startswith('#'):
                    dstat_logger.info(reply)
                elif reply == "":
                    retries -= 1
                    if retries <= 0:
                        raise TransmitError
                else:
                    return reply
        
        n = len(cmd)
        if params is not None:
            n_params = len(params)
            
        for _ in range(retry):
            tries = 5
            while True:
                time.sleep(0.2)
                self.serial.reset_input_buffer()
                self.serial.write('!{}\n'.format(n))
                time.sleep(.1)
                
                try:
                    reply = get_reply()
                except TransmitError:
                    if tries <= 0:
                        continue
                    tries -= 1
                    pass
                else:
                    break
        
            if reply != "@ACK {}".format(n):
                logger.warning("Expected ACK got: {}".format(reply))
                continue
            
            tries = 5
            
            while True:
                self.serial.write('{}\n'.format(cmd))
                try:
                    reply = get_reply()
                except TransmitError:
                    if tries <= 0:
                        continue
                    tries -= 1
                    pass
                else:
                    break
        
            if reply != "@RCV {}".format(n):
                logger.warning("Expected RCV got: {}".format(reply))
                continue

            if params is None:
                return True
            
            tries = 5
            
            while True:
                try:
                    reply = get_reply()
                except TransmitError:
                    if tries <= 0:
                        continue
                    tries -= 1
                    pass
                else:
                    break
                
            if reply != "@RQP {}".format(n_params):
                logger.warning("Expected RQP got: {}".format(reply))
                continue
            
            tries = 5
            
            for i in params:
                while True:
                    self.serial.write(i + " ")
                    try:
                        reply = get_reply()
                        if reply == "@RCVC {}".format(i):
                            break
                    except TransmitError:
                        if tries <= 0:
                            continue
                        tries -= 1
                        pass
                    else:
                        break
            return True
        return False

    def run(self, ser, ctrl_pipe, data_pipe):
        """Execute experiment. Connects and sends handshake signal to DStat
        then sends self.commands. Don't call directly as a process in Windows,
        use run_wrapper instead.
        """
        self.serial = ser
        self.ctrl_pipe = ctrl_pipe
        self.data_pipe = data_pipe
        
        exp_logger.info("Experiment running")
        
        try:
            for i in self.commands:
                status = "DONE"
                if isinstance(i, (str, unicode)):
                    logger.info("Command: %s", i)
                
                    if not self.write_command(i):
                        status = "ABORT"
                        break
            
                else:
                    cmd = i[0]
                    data = i[1]
                
                    logger.info("Command: {}".format(cmd))
                
                    if not self.write_command(cmd, params=data):
                        status = "ABORT"
                        break
                
                if not self.serial_handler():
                    status = "ABORT"
                    break
                
                time.sleep(0.5)
                    
        except serial.SerialException:
            status = "SERIAL_ERROR"
        finally:
            while self.ctrl_pipe.poll():
                self.ctrl_pipe.recv()
        return status
    
    def serial_handler(self):
        """Handles incoming serial transmissions from DStat. Returns False
        if stop button pressed and sends abort signal to instrument. Sends
        data to self.data_pipe as result of self.data_handler).
        """
        scan = 0
        try:
            while True:
                if self.ctrl_pipe.poll():
                    input = self.ctrl_pipe.recv()
                    logger.debug("serial_handler: %s", input)
                    if input == "DISCONNECT":
                        self.serial.write('a')
                        self.serial.reset_input_buffer()
                        logger.info("serial_handler: ABORT pressed!")
                        time.sleep(.3)
                        return False
                    elif input == 'a':
                        self.serial.write('a')
                            
                for line in self.serial:
                    if self.ctrl_pipe.poll():
                        if self.ctrl_pipe.recv() == 'a':
                            self.serial.write('a')
                            
                    if line.startswith('B'):
                        data = self.data_handler(
                                (scan, self.serial.read(size=self.databytes)))
                        data = self.data_postprocessing(data)
                        if data is not None:
                            self.data_pipe.send(data)
                        try:
                            self.datapoint += 1
                        except AttributeError: #Datapoint counting is optional
                            pass
                        
                    elif line.lstrip().startswith('S'):
                        scan += 1
                        
                    elif line.lstrip().startswith("#"):
                        dstat_logger.info(line.lstrip().rstrip())
                                        
                    elif line.lstrip().startswith("@DONE"):
                        dstat_logger.debug(line.lstrip().rstrip())
                        time.sleep(.3)
                        return True
                        
        except serial.SerialException:
            return False
    
    
    def data_handler(self, data_input):
        """Takes data_input as tuple -- (scan, data).
        Returns:
        (scan number, (voltage, current)) -- voltage in mV, current in A
        """
        scan, data = data_input
        voltage, current = struct.unpack('<Hl', data) #uint16 + int32
        return (scan, (
                       (voltage-32768)*(3000./65536)*self.re_voltage_scale,
                       (current+self.gain_trim)*(1.5/8388607)/self.gain
                       )
               )
    
    def store_data(self, incoming, newline):
        """Stores data in data attribute. Should not be called from subprocess.
        Can be overriden for custom experiments."""
        line, data = incoming
        
        if newline is True:
            self.data['current_voltage'].append(deepcopy(self.line_data))

        for i, item in enumerate(self.data['current_voltage'][line]):
            item.append(data[i])
        
    def data_postprocessing(self, data):
        """Discards first data point (usually gitched) by default, can be overridden
        in subclass.
        """
        try:
            if self.datapoint <= 1:
                return None
        except AttributeError: # Datapoint counting is optional
            pass
             
        return data
    
    def scan_process(self, line):
        pass
    
    def experiment_done(self):
        """Runs when experiment is finished (all data acquired)"""
        self.data_to_pandas()
        self.time += [datetime.utcnow()]
    
    def export(self):
        """Return a dict containing data for saving."""
        output = {
                  "datatype" : self.datatype,
                  "xlabel" : self.xlabel,
                  "ylabel" : self.ylabel,
                  "xmin" : self.xmin,
                  "xmax" : self.xmax,
                  "parameters" : self.parameters,
                  "data" : self.data,
                  "commands" : self.commands
                  }
        
        return output

    def data_to_pandas(self):
        """Convert data to pandas DataFrame and set as member of .df
        attribute."""
        self.df = OrderedDict()
        
        for name, data in self.data.items():
            try:
                df = DataFrame(
                    columns=['Scan'] + list(self.plot_format[name]['labels']))
            
                for n, line in enumerate(data):  # Each scan
                    df = df.append(
                        DataFrame(
                            OrderedDict(zip(
                                ['Scan'] + list(self.plot_format[name]['labels']),
                                    [n] + list(line))
                            )
                        ), ignore_index = True
                    )
            except (AttributeError, KeyError):
                try:
                    df = DataFrame(
                        columns=['Scan'] + list(self.columns))
            
                    for n, line in enumerate(data):  # Each scan
                        df = df.append(
                            DataFrame(
                                OrderedDict(zip(
                                    ['Scan'] + list(self.columns),
                                        [n] + list(line))
                                )
                            ), ignore_index = True
                        )
                except AttributeError as e:  # Fallback if no self.columns
                    df = DataFrame(
                        columns=['Scan'] + ["{}{}".format(name, n)
                                            for n in range(len(data))]
                    )
            
                    for n, line in enumerate(data):
                        df = df.append(
                            DataFrame(
                                OrderedDict(zip(
                                    ['Scan'] + ["{}{}".format(name, n)
                                            for n in range(len(data))],
                                        [n] + list(line))
                                )
                            ), ignore_index = True
                        )
            
            self.df[name] = df
            
    def get_info_text(self):
        """Return string of text to disply on Info tab."""
        buf = "#Time: S{} E{}\n".format(self.time[0], self.time[1])
        buf += "#Commands:\n"
        
        for line in self.commands:
            buf += '#{}\n'.format(line)
            
        return buf
    
    def get_save_strings(self):
        """Return dict of strings with experiment parameters and data."""
        buf = {}
        buf['params'] = self.get_info_text()
        buf.update(
            {exp : df.to_csv(sep='\t', encoding='utf-8')
             for exp, df in self.df.items()}
            )
        
        return buf
        
class PlotBox(object):
    """Contains data plot and associated methods."""
    def __init__(self, plots):
        """Initializes plots. self.box should be reparented."""
        self.name = "Main"
        self.continuous_refresh = True
        self.scan_refresh = False
        
        self.plotnames = plots
        self.subplots = {}
        
        self.figure = Figure()
        # self.figure.subplots_adjust(left=0.07, bottom=0.07,
        #                             right=0.96, top=0.96)
        
        self.format_plots() # Should be overriden by subclass
        
        self.figure.set_tight_layout(True)
        
        self.canvas = FigureCanvas(self.figure)
        self.canvas.set_vexpand(True)
        
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.box.pack_start(self.canvas, expand=True, fill=True, padding=0)
    
    def format_plots(self):
        """
        Creates and formats subplots needed. Should be overriden by subclass
        """
        # Calculate size of grid needed
        
        if len(self.plotnames) > 1:
            gs = gridspec.GridSpec(int(ceil(len(self.plotnames)/2.)),2)
        else:
            gs = gridspec.GridSpec(1,1)
        for n, i in enumerate(self.plotnames):
            self.subplots[i] = self.figure.add_subplot(gs[n])
        
        for subplot in self.subplots.values():
            subplot.ticklabel_format(style='sci', scilimits=(0, 3),
                                     useOffset=False, axis='y')
            subplot.plot([],[])
        
    def clearall(self):
        """Remove all lines on plot. """
        for name, plot in self.subplots.items():
            for line in reversed(plot.lines):
                line.remove()
        self.addline()
    
    def clearline(self, subplot, line_number):
        """Remove a single line.
        
        Arguments:
        subplot -- key in self.subplots
        line_number -- line number in subplot
        """
        self.subplots[subplot].lines[line_number].remove()
        
    def addline(self):
        """Add a new line to plot. (initialized with dummy data)))"""
        for subplot in self.subplots.values():
            subplot.plot([], [])
    
    def updateline(self, Experiment, line_number):
        """Update a line specified with new data.
        
        Arguments:
        Experiment -- Experiment instance
        line_number -- line number to update
        """
        for subplot in Experiment.data:
            while True:
                try:
                    self.subplots[subplot].lines[line_number].set_xdata(
                        Experiment.data[subplot][line_number][0])
                    self.subplots[subplot].lines[line_number].set_ydata(
                        Experiment.data[subplot][line_number][1])
                except IndexError:
                    self.addline()
                except KeyError:
                    pass
                else:
                    break
                    # logger.warning("Tried to set line %s that doesn't exist.", line_number)
    def changetype(self, Experiment):
        """Change plot type. Set axis labels and x bounds to those stored
        in the Experiment instance. Stores class instance in Experiment.
        """

        for name, subplot in self.subplots.items():
            subplot.set_xlabel(Experiment.plot_format[name]['labels'][0])
            subplot.set_ylabel(Experiment.plot_format[name]['labels'][1])
            subplot.set_xlim(Experiment.plot_format[name]['xlims'])
        for name, subplot in Experiment.plot_format.items():
            self.subplots[name].set_xlabel(subplot['labels'][0])
            self.subplots[name].set_ylabel(subplot['labels'][1])
            self.subplots[name].set_xlim(subplot['xlims'])

        
        self.figure.canvas.draw()
        
    def redraw(self):
        """Autoscale and refresh the plot."""
        for name, plot in self.subplots.items():
            plot.relim()
            plot.autoscale(True, axis = 'y')
        self.figure.canvas.draw()

        return True
import time
import struct
import numpy as np
import serial

from .experiment_template import PlotBox, Experiment, exp_logger

class ChronoampBox(PlotBox):
    def format_plots(self):
        """
        Creates and formats subplots needed. Overrides superclass.
        """
        self.subplots = {'current_time' : self.figure.add_subplot(111)}
        
        for key, subplot in self.subplots.items():
            subplot.ticklabel_format(style='sci', scilimits=(0, 3),
                                     useOffset=False, axis='y')
            subplot.plot([],[])
        
class Chronoamp(Experiment):
    id = 'cae'
    """Chronoamperometry experiment"""
    def setup(self):
        self.plots.append(ChronoampBox('current_time'))
        
        self.datatype = "linearData"
        self.datalength = 2
        self.databytes = 8
        self.data = {'current_time' : [([],[])]}
        self.columns = ['Time (s)', 'Current (A)']
        self.plot_format = {
                            'current_time' : {
                                'labels' : self.columns,
                                'xlims' : (0, sum(self.parameters['time']))
                                }
                            }
        
        self.commands.append(
            ("ER"+ str(len(self.parameters['potential'])) + " 0 ", [])
            )

        for i in self.parameters['potential']:
            self.commands[-1][1].append(str(int(i*(65536./3000)+32768)))
        for i in self.parameters['time']:
            self.commands[-1][1].append(str(i))
      
    def data_handler(self, data_input):
        """Overrides Experiment method to not convert x axis to mV."""
        scan, data = data_input
        # 2*uint16 + int32
        seconds, milliseconds, current = struct.unpack('<HHl', data)
        return (scan, (
                       seconds+milliseconds/1000.,
                       (current+self.gain_trim)*(1.5/self.gain/8388607)
                       )
                )

    def store_data(self, incoming, newline):
        """Stores data in data attribute. Should not be called from subprocess.
        Can be overriden for custom experiments."""
        line, data = incoming
        
        if newline is True:
            self.data['current_time'].append(deepcopy(self.line_data))

        for i, item in enumerate(self.data['current_time'][line]):
            item.append(data[i])
                
class PDExp(Chronoamp):
    """Photodiode/PMT experiment"""
    id = 'pde'
    def setup(self):
        self.plots.append(ChronoampBox('current_time'))
        
        self.datatype = "linearData"
        self.datalength = 2
        self.databytes = 8
        self.data = {'current_time' : [([],[])]}
        self.columns = ['Time (s)', 'Current (A)']
        self.plot_format = {
                            'current_time' : {
                                'labels' : self.columns,
                                'xlims' : (0, int(self.parameters['time']))
                                }
                            }

        if self.parameters['shutter_true']:
            if self.parameters['sync_true']:
                self.commands.append("EZ")
                self.commands[-1] += str(self.parameters['sync_freq'])
                self.commands[-1] += " "
            else:
                self.commands.append(("E2", []))

        command = "ER1 "
        params = []

        if self.parameters['interlock_true']:
            command += "1 "
        else:
            command += "0 "
            
        if self.parameters['voltage'] == 0: # Special case where V=0
            params.append("65535")
        else:
            params.append(str(int(
                            65535-(self.parameters['voltage']*(65536./3000))))
                            )
        params.append(str(self.parameters['time']))

        self.commands.append((command, params))

        if self.parameters['shutter_true']:
            if self.parameters['sync_true']:
                self.commands.append("Ez")
            else:
                self.commands.append("E1")
                
class FT_Box(PlotBox):
    def updateline(self, Experiment, line_number):
        def search_value(data, target):
            for i in range(len(data)):
                if data[i] > target:
                    return i
        
        y = Experiment.data['data'][line_number][1]
        x = Experiment.data['data'][line_number][0]
        freq = Experiment.parameters['adc_rate_hz']
        i = search_value(x, float(Experiment.parameters['fft_start']))
        y1 = y[i:]
        x1 = x[i:]
        avg = mean(y1)
        min_index, max_index = findBounds(y1)
        y1[min_index] = avg
        y1[max_index] = avg
        f, Y = plotSpectrum(y1[min_index:max_index],freq)
        self.axe1.lines[line_number].set_ydata(Y)
        self.axe1.lines[line_number].set_xdata(f)
        Experiment.data['ft'] = [(f, Y)]
        
    def changetype(self, Experiment):
        """Change plot type. Set axis labels and x bounds to those stored
        in the Experiment instance. Stores class instance in Experiment.
        """
        self.axe1.set_xlabel("Freq (Hz)")
        self.axe1.set_ylabel("|Y| (A/Hz)")
        self.axe1.set_xlim(0, Experiment.parameters['adc_rate_hz']/2)
        
        Experiment.plots['ft'] = self

        self.figure.canvas.draw()
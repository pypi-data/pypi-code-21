import time
import struct

from .experiment_template import PlotBox, Experiment

class PotBox(PlotBox):
    def format_plots(self):
        """
        Creates and formats subplots needed. Overrides superclass.
        """
        self.subplots = {'voltage_time' : self.figure.add_subplot(111)}
        
        for key, subplot in self.subplots.items():
            subplot.ticklabel_format(style='sci', scilimits=(0, 3),
                                     useOffset=False, axis='y')
            subplot.plot([],[])
                                     
class PotExp(Experiment):
    id = 'pot'
    """Potentiometry experiment"""
    def setup(self):
        self.plots.append(PotBox(['voltage_time']))
        
        self.datatype = "linearData"
        self.datalength = 2
        self.databytes = 8
        self.data = {'voltage_time' : [([],[])]}
        self.columns = ['Time (s)', 'Voltage (V)']
        self.plot_format = {
                            'voltage_time' : {
                                'labels' : self.columns,
                                'xlims' : (0, int(self.parameters['time']))
                                }
                            }
        
        self.commands += "E"
        self.commands[2] += "P"
        self.commands[2] += str(self.parameters['time'])
        self.commands[2] += " 1 " #potentiometry mode

    def data_handler(self, data_input):
        """Overrides Experiment method to not convert x axis to mV."""
        scan, data = data_input
        # 2*uint16 + int32
        seconds, milliseconds, voltage = struct.unpack('<HHl', data)
        return (scan, (
                       seconds+milliseconds/1000.,
                       voltage*self.re_voltage_scale*(1.5/8388607.)
                       )
                )

    def store_data(self, incoming, newline):
        """Stores data in data attribute. Should not be called from subprocess.
        Can be overriden for custom experiments."""
        line, data = incoming
        
        if newline is True:
            self.data['voltage_time'].append(deepcopy(self.line_data))

        for i, item in enumerate(self.data['voltage_time'][line]):
            item.append(data[i])
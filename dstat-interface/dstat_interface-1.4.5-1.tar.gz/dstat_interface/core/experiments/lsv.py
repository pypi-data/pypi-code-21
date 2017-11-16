import time
import struct

from .experiment_template import PlotBox, Experiment
                                     
class LSVExp(Experiment):
    """Linear Scan Voltammetry experiment"""
    id = 'lsv'
    def setup(self):
        super(LSVExp, self).setup()
        
        self.datatype = "linearData"
        self.datalength = 2
        self.databytes = 6  # uint16 + int32
        self.plot_format['current_voltage']['xlims'] = tuple(
                    sorted(
                        (int(self.parameters['start']),
                         int(self.parameters['stop']))
                           )
                )
        
        self.commands += "E"
        self.commands[2] += "L"
        self.commands[2] += str(self.parameters['clean_s'])
        self.commands[2] += " "
        self.commands[2] += str(self.parameters['dep_s'])
        self.commands[2] += " "
        self.commands[2] += str(int(
                                    int(self.parameters['clean_mV'])/
                                    self.re_voltage_scale*
                                    (65536./3000)+32768
                                ))
        self.commands[2] += " "
        self.commands[2] += str(int(
                                    int(self.parameters['dep_mV'])/
                                    self.re_voltage_scale*
                                    (65536./3000)+32768
                                ))
        self.commands[2] += " "
        self.commands[2] += str(int(
                                    int(self.parameters['start'])/
                                    self.re_voltage_scale*
                                    (65536./3000)+32768
                                ))
        self.commands[2] += " "
        self.commands[2] += str(int(
                                    int(self.parameters['stop'])/
                                    self.re_voltage_scale*
                                    (65536./3000)+32768
                                ))
        self.commands[2] += " "
        self.commands[2] += str(int(
                                    int(self.parameters['slope'])/
                                    self.re_voltage_scale*
                                    (65536./3000)
                                ))
        self.commands[2] += " "
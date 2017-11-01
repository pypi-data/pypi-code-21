"""Defines the primary class for the ILAMB BMI."""

import os
import subprocess
from basic_modeling_interface import Bmi
from .config import Configuration


class BmiIlamb(Bmi):

    _component_name = 'ILAMB'
    _command = 'ilamb-run'
    _args = None

    def __init__(self):
        self._time = self.get_start_time()
        self.config = Configuration()

    @property
    def args(self):
        return [self._command] + (self._args or [])

    def get_component_name(self):
        return self._component_name

    def initialize(self, filename):
        self.config.load(filename)
        os.environ['ILAMB_ROOT'] = self.config.get_ilamb_root()
        os.environ['MPLBACKEND'] = 'Agg'
        self._args = self.config.get_arguments()

    def update(self):
        try:
            with open('log', 'w') as fp:
                subprocess.check_call(self.args,
                                      stdout=fp,
                                      stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print 'Error in running ILAMB. Command:\n' + ' '.join(e.cmd)
        finally:
            self._time = self.get_end_time()

    def update_until(self, time):
        self.update()

    def finalize(self):
        pass

    def get_input_var_names(self):
        return ()

    def get_output_var_names(self):
        return ()

    def get_start_time(self):
        return 0.0

    def get_end_time(self):
        return 1.0

    def get_current_time(self):
        return self._time

    def get_time_step(self):
        return 1.0

    def get_time_units(self):
        return 's'

    def __str__(self):
        s = ' '.join(self.args)
        return s

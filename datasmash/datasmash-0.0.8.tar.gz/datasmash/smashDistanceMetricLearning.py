import os
import pdb
import uuid
import atexit
import sys
import subprocess as sp
import numpy as np
from numpy import nan
import pandas as pd
from datasmash.utils import write_series, preprocess_map, quantizer
from datasmash.primitive_interfaces.transformer import TransformerPrimitiveBase
from datasmash.config import CWD, TEMP_DIR, BIN_PATH


class SmashDistanceMetricLearning(TransformerPrimitiveBase):
    '''
    Object for running Data Smashing  to calculate the distance matrix between
    multiple timeseries; Inherits from UnsupervisedSeriesLearningBase API

    Inputs -
        bin_path(string): Path to Smash binary as a string
        input_class (Input Object): Input data

    Attributes:
        bin_path (string): path to bin/smash
    '''

    def __init__(self, bin_path=BIN_PATH):
        self.__bin_path = os.path.abspath(bin_path)
        prev_wd = os.getcwd()
        os.chdir(CWD)
        sp.Popen("mkdir "+ TEMP_DIR, shell=True, stderr=sp.STDOUT).wait()
        self.__file_dir = CWD + "/" + TEMP_DIR
        os.chdir(prev_wd)
        self._problem_type = "distance_metric_learning"
        self.__input_dm_fh = None
        self.__input_dm_fname = None
        self.__output_dm_fname = None
        self.__command = (self.__bin_path + "/smash")
        self._output = None

    def set_training_data(self, input_data):
        self.__quantized_data = preprocess_map(quantizer, input_data)

    def _get_dm(self, quantized, first_run, max_len=None, num_get_dms=5, details=False):
        '''
        Helper function:
        Calls bin/smash to compute the distance matrix on the given input
        timeseries and write I/O files necessary for Data Smashing

        Inputs -
            max_len (int): max length of data to use
            num_get_dms (int): number of runs of Smash to compute distance
                matrix (refines results)
            details (boolean): do (True) or do not (False) show cpu usage of
                Data Smashing algorithm

        Outuputs -
            (numpy.ndarray) distance matrix of the input timeseries
            (shape n_samples x n_samples)
        '''

        if not first_run:
            os.unlink(self.__input_dm_fh.name)
            self.__command = (self.__bin_path + "/smash")

        self.__input_dm_fh, self.__input_dm_fname = write_series(input_data=self.__quantized_data,\
                                                                    file_dir=self.__file_dir)

        self.__command += " -f " + self.__input_dm_fname + " -D row -T symbolic"

        if max_len is not None:
            self.__command += (" -L " + str(max_len))
        if num_get_dms is not None:
            self.__command += (" -n " + str(num_get_dms))
        if not details:
            self.__command += (" -t 0")

        self.__output_dm_fname = str(uuid.uuid4())
        self.__output_dm_fname = self.__output_dm_fname.replace("-", "")
        self.__command += (" -o " + self.__output_dm_fname)

        prev_wd = os.getcwd()
        os.chdir(self.__file_dir)
        sp.Popen(self.__command, shell=True, stderr=sp.STDOUT).wait()
        os.chdir(prev_wd)

        try:
            results = np.loadtxt(fname=(self.__file_dir +"/"+self.__output_dm_fname), dtype=float)
            return results
        except IOError:
            print("Error: Smash calculation unsuccessful. Please try again.")


    def produce(self, ml=None, nr=None, d=False):
        '''
        Uses Data Smashing to compute the distance matrix of the timeseries

        Inputs -
            ml (int): max length of data to use
            nr (int): number of runs of Smash to compute distance matrix
                (refines results)
            d (boolean): do (True) or do not (False) show cpu usage of Data
            Smashing algorithm

        Outuputs -
            (numpy.ndarray) distance matrix of the input timeseries
            (shape n_samples x n_samples)
        '''

        if self.__input_dm_fh is None:
            self._output = self._get_dm(True, True, ml, nr, d)
            return self._output
        else:
            self._output = self._get_dm(True, False, ml, nr, d)
            return self._output


def cleanup():
    '''
    Maintenance function:
    Clean up library files before closing the script; no I/O
    '''

    prev_wd = os.getcwd()
    os.chdir(CWD)
    if os.path.exists(CWD + "/" + TEMP_DIR):
        command = "rm -r " + CWD + "/" + TEMP_DIR
        sp.Popen(command, shell=True, stderr=sp.STDOUT).wait()
    os.chdir(prev_wd)


atexit.register(cleanup)

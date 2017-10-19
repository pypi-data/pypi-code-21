import os
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


class SmashEmbedding(TransformerPrimitiveBase):
    '''
    Object for running Data Smashing to calculate the distance matrix between
        timeseries and using Sippl and/or sklearn.manifold.MDS to embed;
        inherits from the UnsupervisedSeriesLearningBase API

    Inputs -
        bin_path(string): Path to Data Smashing binary as a string
        input_class (Input Object): Input data
        n_dim (int): number of dimensions for embedding algorithm
        embed_class (class): custom class to embed input timeseries

    Attributes:
        bin_path (string): path to bin/smash
        num_dimensions (int): number of dimensions to use for embedding
        embedding_class (class): custom class to embed input timeseries
    '''

    def __init__(self, bin_path=BIN_PATH, n_dim=2, embed_class=None):
        self.__bin_path = os.path.abspath(bin_path)
        self.__num_dimensions = n_dim
        self.__embedding_class = embed_class
        prev_wd = os.getcwd()
        os.chdir(CWD)
        sp.Popen("mkdir "+ TEMP_DIR, shell=True, stderr=sp.STDOUT).wait()
        self.__file_dir = CWD + "/" + TEMP_DIR
        os.chdir(prev_wd)
        self._problem_type = "embedding"
        self.__input_dm_fh = None
        self.__input_dm_fname = None
        self.__output_dm_fname = None
        self.__command = (self.__bin_path + "/smash")
        self._output = None
        self.__input_e = None

    def set_training_data(self, input_data):
        self.__quantized_data = preprocess_map(quantizer, input_data)

    def _run_dm(self, first_run_dm, max_len=None, num_run_dms=5, details=False):
        '''
        Helper function:
        Calls bin/smash to compute the distance matrix on the given input
        timeseries and write I/O files necessary for Data Smashing

        Inputs -
            max_len (int): max length of data to use
            num_run_dms (int): number of runs of Smash to compute distance
                matrix (refines results)
            details (boolean): do (True) or do not (False) show cpu usage of
                Data Smashing algorithm

        Outuputs -
            (numpy.ndarray) distance matrix of the input timeseries
            (shape n_samples x n_samples)
        '''

        if not first_run_dm:
            os.unlink(self.__input_dm_fh.name)
            self.__command = (self.__bin_path + "/smash")

        self.__input_dm_fh, self.__input_dm_fname = write_series(input_data=self.__quantized_data,\
                                                                    file_dir=self.__file_dir)

        self.__command += " -f " + self.__input_dm_fname + " -D row -T symbolic"

        if max_len is not None:
            self.__command += (" -L " + str(max_len))
        if num_run_dms is not None:
            self.__command += (" -n " + str(num_run_dms))
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
            results = np.loadtxt(fname=\
            (self.__file_dir +"/"+self.__output_dm_fname), dtype=float)
            return results
        except IOError:
            print("Error: Smash calculation unsuccessful. Please try again.")


    def _fit_asymmetric(self, y=None, init=None):
        '''
        Helper method:
        Transforms distance matrix data to be symmetric and compatible with
        sklearn embedding

        Inputs -
            y and init (numpy.ndarray): parameters of sklearn fit methods

        Returns -
            (None): modifies instance in place
        '''

        self._output = self._output.astype(np.float64)
        try:
            self.__embedding_class.fit(self._output, y, init)
        except ValueError:
            self._output = self._output + self._output.T
            try:
                self.__embedding_class.fit(self._output, y, init)
            except:
                warnings.warn(\
                "Embedding error: Unable to fit. \
                Please ensure input embedding class takes\
                distance matrices as input.")

    def _fit(self, ml=None, nr=None, d=False, y=None, init=None):
        '''
        Uses Data Smashing to compute the distance matrix of the timeseries;
            if an embedding class has been defined, then fit on that
            embedding class will be run on the distance matrix

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
            self._output = self._run_dm(True, ml, nr, d)
            if self.__embedding_class is not None:
                self._fit_asymmetric(y, init)
            return self._output
        else:
            self._output = self._run_dm(False, ml, nr, d)
            if self.__embedding_class is not None:
                self._fit_asymmetric(y, init)
            return self._output

    def produce(self, ml=None, nr=None, d=False, \
    embedder='default', y=None, init=None):
        '''
        Computes Data Smashing distance matrix and returns
        the resulting embedded coordinates

        Inputs -
            ml (int): max length of data to use
            nr (int): number of runs of Smash to compute distance matrix
                (refines results)
            d (boolean): do (True) or do not (False) show cpu usage of Smash
                algorithm
            embedder (string) either 'default' to use Sippl Embedding or
                'custom' to use user-defined emebedding class
            y and init (numpy.ndarray): parameters for the fit_transform method
                of sklearn.embedding classes

        Outuputs -
            (numpy.ndarray) the embedded coordinates of the input data
            (shape num_timeseries x num_dimensions)
        '''

        self.__input_e = self._fit(ml, nr, d)
        # since you run fit, the assumption can read in from the file you wrote out to in fit
        # i.e. self.__output_dm_fname is the name for the input

        if embedder == 'default':
            prev_wd = os.getcwd()
            os.chdir(self.__file_dir)
            command = (self.__bin_path + "/embed -f ")

            if os.path.isfile(self.__output_dm_fname):
                command += self.__output_dm_fname
            else: # should be impossible
                print("Smash Embedding encountered an error. Please try again.")
                sys.exit(1)

            if not d:
                FNULL = open(os.devnull, 'w')
                sp.Popen(command, shell=True, stdout=FNULL, stderr=sp.STDOUT,\
                 close_fds=True).wait()
            else:
                sp.Popen(command, shell=True, stderr=sp.STDOUT).wait()

            try:
                sippl_embed = np.loadtxt(fname="outE.txt", dtype=float)
                if self.__num_dimensions > sippl_embed.shape[1]:
                    raise ValueError("Error: Number of dimensions specified \
                    greater than dimensions of input data")
                sippl_feat = sippl_embed[:, :self.__num_dimensions]
                os.chdir(prev_wd)
                self._output = sippl_feat
                return self._output
            except IOError or IndexError:
                print("Error: Embedding unsuccessful. Please try again.")
        else:
            self.__input_e = self.__input_e.astype(np.float64)
            try:
                self._output = self.__embedding_class.fit_transform(\
                self.__input_e, y, init)
                return self._output

            except ValueError:
                self.__input_e = self.__input_e + self.__input_e.T
                try:
                    self._output = self.__embedding_class.fit_transform(self.__input_e, y,\
                    init)
                    return self._output
                except:
                    warnings.warn(\
                    "Embedding error: please ensure input embedding class takes\
                    distance matrices as input.")
                    return None


    def transform(self, ml=None, nr=None, d=False, \
    embedder='default', init=None):
        '''
        Returns the resulting embedded coordinates from the fitted embedding class

        Inputs -
            ml (int): max length of data to use
            nr (int): number of runs of Smash to compute distance matrix
                (refines results)
            d (boolean): do (True) or do not (False) show cpu usage of Smash
                algorithm
            embedder (string) either 'default' to use Sippl Embedding or
                'custom' to use user-defined emebedding class
            y and init (numpy.ndarray): parameters for the fit_transform method
                of sklearn.embedding classes

        Outputs -
            (numpy.ndarray) the embedded coordinates of the input data
            (shape num_timeseries x num_dimensions)
        '''

        assert self._output is not None, \
        "Error: no embedding class has been fit"
        if embedder == 'default':
            prev_wd = os.getcwd()
            os.chdir(self.__file_dir)
            command = (self.__bin_path + "/embed -f ")

            if os.path.isfile(self.__output_dm_fname):
                command += self.__output_dm_fname
            else: # should be impossible
                print("Smash Embedding encountered an error. Please try again.")
                sys.exit(1)

            if not d:
                FNULL = open(os.devnull, 'w')
                sp.Popen(command, shell=True, stdout=FNULL, stderr=sp.STDOUT,\
                 close_fds=True).wait()
            else:
                sp.Popen(command, shell=True, stderr=sp.STDOUT).wait()

            try:
                sippl_embed = np.loadtxt(fname="outE.txt", dtype=float)
                if self.__num_dimensions > sippl_embed.shape[1]:
                    raise ValueError("Error: Number of dimensions specified \
                    greater than dimensions of input data")
                sippl_feat = sippl_embed[:, :self.__num_dimensions]
                os.chdir(prev_wd)
                self._output = sippl_feat
                return self._output
            except IOError or IndexError:
                print("Error: Embedding unsuccessful. Please try again.")
        else:
            self._output = self._output.astype(np.float64)
            try:

                try:
                    y_ = self._data_additional.data
                except AttributeError:
                    y_ = None

                self._output = self.__embedding_class.transform(\
                self._ouput, y_, init)
                return self._output

            except ValueError:
                self._ouput = self._ouput + self._ouput.T

                try:
                    y_ = self._data_additional.data
                except AttributeError:
                    y_ = None

                try:
                    self._output = self.__embedding_class.transform(self._ouput, y_,\
                    init)
                    return self._output
                except:
                    warnings.warn(\
                    "Embedding error: please ensure input embedding class takes\
                    distance matrices as input.")
                    return None


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

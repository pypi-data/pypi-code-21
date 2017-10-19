import os
import sys
import time
import csv
import math
import uuid
import atexit
import pdb
import warnings
import subprocess as sp
import numpy as np
from numpy import nan
import pandas as pd
from datasmash.utils import *
from datasmash.primitive_interfaces.supervised_learning import SupervisedLearnerPrimitiveBase
from datasmash.config import TEMP_DIR, PREFIX, CWD, BIN_PATH


class LibFile:
    '''
    Helper class to store library file information to interface with
    file-I/O data smashing code

    Attributes -
        class (int):  label given to the class by SmashMatch
            based on the order in which it was fed in
        label (int): actual class label set by user
        filename (string): path to temporary library file
    '''
    def __init__(self, class_, label_, fname_):
        self.class_name = class_
        self.label = label_
        self.filename = fname_


class SmashClassification(SupervisedLearnerPrimitiveBase):
    '''
    Class for SmashMatch-based classification; I/O modeled after
    sklearn.SVM.SVC classifier and inherits from
     SupervisedLearningPrimitiveBase

    Inputs -
        bin_path(string): Path to smashmatch as a string
        preproc (function): function to quantize timeseries;

    Attributes:
        bin_path(string): Path to smashmatch as a string
        classes (np.1Darray): class labels fitted into the model;
            also column headers for predict functions
            NOTE: cannot be changed once fitted - rerun fit to use new classes
        preproc (function): quantization function for timeseries data
    '''
    # lib_files = list of library file names or LibFile Objects
    def __init__(self, bin_path=BIN_PATH, preproc=quantizer):
        assert os.path.isfile(bin_path + 'smashmatch'), "Error: invalid bin path."
        self.__bin_path = os.path.abspath(bin_path + 'smashmatch')
        prev_wd = os.getcwd()
        os.chdir(CWD)
        sp.Popen("mkdir "+ PREFIX, shell=True, stderr=sp.STDOUT).wait()
        self.__file_dir = CWD + "/" + PREFIX
        os.chdir(prev_wd)
        self.__classes = []
        self.__lib_files = [] # list of LibFile objects
        self.__lib_command = " -F "
        self.__command = self.__bin_path
        self.__input = None
        self.__mapper = {}
        self.__preproc = preproc

    def _get_unique_name(self, lib):
        '''
        Helper method:
        Generates unique filename with the TEMP_DIR "lib_" if the input
            file is a library files or no TEMP_DIR if it is not a library file

        Inputs -
            lib (boolean) whether the generated name is for a library file (True)
            or for an input file (False)

        Outputs -
            unique_name
        '''
        rv = str(uuid.uuid4())
        rv = rv.replace("-", "")
        if lib:
            return "lib_" + rv
        else:
            return "input_" + rv

    def _make_libs_df(self, X, y):
        '''
        Helper method:
        Writes out class labels & examples to files usable by SmashMatch
            (delimited by spaces, each row is a timeseries, create a different file for each series)

        Inputs -
            X (pd.DataFrame): timeseries examples of each class, each row is a
                timeseries
            y (pd.Dataframe): labels for each timeseries

        Returns -
            lib_files (list of LibFile objects)
        '''
        if "level" not in X.columns:
            X.insert(0, "level", y)

        X.sort_values("level")

        labels = y.unique().tolist()
        class_num = 0

        lib_files = []
        for label_ in labels:
            df = X.loc[X.level == label_]
            df = df.drop("level", 1)
            fname = self._get_unique_name(True)
            write_series(input_data=df, file_dir=self.__file_dir, filename=fname)
            lib_files.append(LibFile(class_num, label_, fname))
            class_num += 1
        return lib_files

    def _make_libs(self, X, y):
        '''
        Helper method:
        Writes out class labels & examples to files usable by SmashMatch
            (delimited by spaces, each row is a timeseries, create a different file for each series)

        Inputs -
            X (np.nda): timeseries examples of each class, each row is a
                timeseries
            y (np.1da): labels for each timeseries

        Returns -
            rv (list of LibFile objects)
        '''
        rv = []
        merged = np.c_[y, X] # merge to one large np array with labels at col 0
        merged = merged[np.argsort(merged[:, 0])] # sort in ascending order by col 0
        libs = np.split(merged, np.where(np.diff(merged[:,0]))[0]+1) # split ndas by class

        class_num = 0
        for class_ in libs:
            label_ = class_[0, 0]
            rows = []
            for stream in class_:
                rows.append(stream[1:].tolist()) # cut off label from row entry
            lib_f = self.get_lib_nameunique_name(True)
            with open(lib_f, "w") as f:
                wr = csv.writer(f, delimiter=" ")
                wr.writerows(rows)
            rv.append(LibFile(class_num, label_, lib_f))
            class_num += 1
        return rv

    def _write_series_nda(self, array):
        '''
        Helper method:
        Writes out input data to file usable by SmashMatch (delimited by space)
            each row is a timeseries

        Inputs -
            array (np.nda): data to be classified; each row = unique timeseries

        Outputs -
            (string) filename of the input_file
        '''
        self.__input = array.astype(np.int32)
        rows = array.tolist()
        to_write = []
        for row in rows:
            to_write.append( [int(x) for x in row if not pd.isnull(x)] )
        fname = self._get_unique_name(False)
        with open(self.__file_dir + "/" + fname, "w") as f:
            wr = csv.writer(input_fh, delimiter=" ")
            wr.writerows(to_write)
        return fname

    def _compute(self, X, input_length, num_repeats, no_details, force):
        '''
        Helper method:
        Calls SmashMatch on the specified data with the parameters specified;
            creates command string for SmashMatch binary and calls using
            SmashMatch; udpates internal variables

        Inputs -
            X (numpy.ndarray or pandas DataFrame): input data (each row is a
                different timeseries)
            input_length (int): length of the input timeseries to use
            num_repeats (int): number of times to run SmashMatch (for refining
                results)
            no_details (boolean): do not print SmashMatch processer usage and
                speed while running classification
            force (boolean): force re-classification on current dataset

        Outputs -
            (boolean) whether SmashMatch results corresponding to X were created/exist
        '''
        if force or self._should_calculate(X): # dataset was not the same as before or first run
            if force:
                self._reset_input()

            if isinstance(X, np.ndarray):
                self.__input = X
                input_name_command = " -f " + self._write_series_nda(X)
            elif isinstance(X, pd.DataFrame): # being explicit
                self.__input = X
                fname = self._get_unique_name(False)
                write_series(input_data=X, file_dir=self.__file_dir, filename=fname)
                input_name_command = " -f " + fname
            else: # theoretically should be impossible, but to be explicit
                raise ValueError("Error: unsupported types for X. X can only be of type \
                numpy.ndarray or pandas.DataFrame.")

            if input_length is not None:
                input_length_command = " -x " + str(input_length)

            self.__command += (input_name_command + self.__lib_command + "-T symbolic -D row ")
            self.__command += ("-L true true true -o " + TEMP_DIR + " -d false")
            self.__command += (" -n " + str(num_repeats))

            if input_length is not None:
                self.__command += input_length_command
            if no_details:
                self.__command += " -t 0"

            os.chdir(self.__file_dir)
            sp.Popen(self.__command, shell=True, stderr=sp.STDOUT).wait()
            os.chdir(CWD)

            if not self._has_smashmatch(): # should theoretically be impossible \
            # to return False, but for safety
                return False
            else: # successfully ran smashmatch to get results
                return True
        else: # dataset was the same as before, use existing result files
            return True

    def _reset_input(self):
        '''
        Helper Method:
        Clears the working data directory of previous run of SmashMatch and
            resets command to be fed into SmashMatch; no I/O
        '''
        os.chdir(self.__file_dir)
        sp.Popen("rm input_*", shell=True, stderr=sp.STDOUT).wait()
        sp.Popen("rm " + TEMP_DIR + "*", shell=True, stderr=sp.STDOUT).wait()
        self.__command = self.__bin_path
        os.chdir(CWD)

    def _has_smashmatch(self):
        '''
        Helper method:
        Checks internal data directory for SmashMatch result files

        Input -
            (None)
        Output -
            (boolean) True if SmashMatch files present, False if SmashMatch
                files aren't present
        '''
        if TEMP_DIR + "_prob" in os.listdir(self.__file_dir) and \
        TEMP_DIR + "_class" in os.listdir(self.__file_dir):
            return True
        else:
            return False

    def _should_calculate(self, X_):
        '''
        Helper method:
        Determines case of current use then decides whether or not to clear
            data directory of files to prevent hogging space

        Inputs -
            X_ (numpy.ndarray or pandas.DataFrame): timeseries data

        Returns -
            True if results were cleared or interrupted and SmashMatch needs to
                be run again, False if first run or if dataset is the same
                since SmashMatch produces both the outputs of predict and predict_log_proba per every call
        '''
        # pdb.set_trace()
        # because using a np compare, have to catch self.__input = None first
        # will happen on first try
        if self.__input is None:
            return True

        if isinstance(X_, np.ndarray):
            # assuming if previous run had diff input type then now new input data
            if isinstance(self.__input, pd.DataFrame):
                self._reset_input()
                return True
            # don't clear results if same dataset: don't run again
            elif isinstance(self.__input, np.ndarray) and \
            np.array_equal(X_, self.__input):
                if _has_smashmatch():
                    return False
                else: # user cancelled half-way is running ont he same input
                    return True
            # implied self.__input != X_
            elif isinstance(self.__input, np.ndarray) and \
            not np.array_equal(X_, self.__input):
                if _has_smashmatch():
                    self._reset_input()
                    return True
                else: # user decided to cancel half-way and run on diff dataset
                    return True
        elif isinstance(X_, pd.DataFrame):
            if isinstance(self.__input, np.ndarray):
                self._reset_input()
                return True
            elif isinstance(self.__input, pd.DataFrame) and \
            self.__input.equals(X_):
                if self._has_smashmatch():
                    return False
                else: # re-run on the same data but user possibly cancelled half-way through
                    return True
            elif isinstance(self.__input, pd.DataFrame) and \
            not self.__input.equals(X_):
                if self._has_smashmatch():
                    self._reset_input()
                    return True
                else:
                    return True
        else: # checking cases of type
            raise ValueError("Error: unsupported types for X. X can only be of type \
            numpy.ndarray or pandas.DataFrame.")

    def _clean_libs(self):
        '''
        Helper method:
        Removes files created by reading and writing library files and clears
        relevant internally stored variables; no I/O
        '''
        os.chdir(self.__file_dir)
        sp.Popen("rm lib_*", shell=True, stderr=sp.STDOUT).wait()
        os.chdir(CWD)
        self.__classes = []
        self.__lib_files = []
        self.__lib_command = " -F "

    ### Main methods ###
    def set_training_data(self, input_data):
        self.X, self.y = condense(input_data)

    def fit(self, quantize=False):
        '''
        Reads in appropriate data/labels -> library class files
            to be used by SmashMatch
            (writes out library files in format usable by SmashMatch)

        Inputs -
            X (np.nda or pandas.DataFrame): class examples
            y (np.1da or pandas.Series): class labels
            quantize (boolean): if timeseries have not beeen quantized,
                apply instantiated quantizer to input timeseries examples

        Returns -
          (None) modifies object in place
        '''
        if quantize:
            assert(self.__preproc is not None), "Error: no quantization function defined"
            self.X = preprocess_map(self.__preproc, self.X)
        # delete old library files before running (would only be true after first run)
        len_libs = len(self.__lib_files)
        if len_libs != 0:
            self._clean_libs()

        if isinstance(self.X, np.ndarray):
            self.__lib_files = self._make_libs(self.X, self.y)
        elif isinstance(self.X, pd.DataFrame):
            self.__lib_files = self._make_libs_df(self.X, self.y)
        else:
            raise ValueError("Error: unsupported types for X. X can only be of type numpy.ndarray or pandas.DataFrame.")

        mappings = []
        # need to make sure we feed the class_names in according to their actual order
        for lib in self.__lib_files:
            mappings.append((lib.class_name, lib))
        mappings.sort(key=lambda x: x[0])
        for mapping in mappings:
            self.__mapper[mapping[0]] = mapping[1] # key = class_num, value = LibFile
            self.__classes.append(mapping[1].label)
            self.__lib_command += mapping[1].filename + ' ' # should return only the filename
        self.__classes = np.asarray(self.__classes)
        return

    def produce(self, x, il=None, nr=5, no_details=True, force=False, quantize=False):
        '''
        Classifies each input timeseries (X) using SmashMatch and the given parameters

        Inputs -
            x (numpy.nda or pandas.DataFrame): input data (each row is a
                different timeseries)
            il (int): length of the input timeseries to use
            nr (int): number of times to run SmashMatch (for refining results)
            no_details (boolean): do not print SmashMatch cpu usage/speed of
                algorithm while running clasification
            force (boolean): force re-classification on current dataset
            quantize (boolean): if input timeseries have not beeen quantized,
                apply class quantizer to input timeseries

        Outputs -
            numpy.nda of shape (num_timeseries), 1 if successful or None if not successful
        '''
        if quantize:
            assert(self.__preproc is not None), "Error: no quantization function defined"
            x = preprocess_map(self.__preproc, x)

        compute_res = self._compute(x, il, nr, no_details, force)
        if compute_res:
            class_path = self.__file_dir + "/" + TEMP_DIR + "_class"
            with open(class_path, 'r') as f:
                raw = f.read().splitlines()
            formatted = []
            for result in raw:
                formatted.append(self.__mapper[int(result)].label) # should append labels in order
            res = np.asarray(formatted)

            # return np.reshape(res, (-1, 1))
            return res
        else:
            print("Error processing command: SmashMatch FNF. Please try again.")
            return None

    def produce_proba(self, x, il=None, nr=5, no_details=True, force=False, quantize=False):
        '''
        Predicts percentage probability for the input time series to classify as any of the possible classes fitted

        Inputs -
            x (numpy.nda or pandas.DataFrame): input data (each row is a
                different timeseries)
            il (int): length of the input timeseries to use
            nr (int): number of times to run SmashMatch (for refining results)
            no_details (boolean): do not print SmashMatch cpu usage/speed of
                algorithm while running clasification
            force (boolean): force re-classification on current dataset
            quantize (boolean): if input timeseries have not been quantized,
                apply class quantizer to input timeseries

        Outputs -
            np.nda of shape n x m if successful or None if not successful
                where n = number of timeseries and m = number of classes
                probabilities are listed in an order corresponding to the classes attribute
        '''
        if quantize:
            assert(self.__preproc is not None), "Error: no quantization function defined"
            x = preprocess_map(self.__preproc, x)

        compute_res = self._compute(x, il, nr, no_details, force)
        if compute_res:
            class_path = self.__file_dir + "/" + TEMP_DIR + "_prob"
            probs = np.loadtxt(fname=class_path, dtype=float)
            return probs
        else:
            print("Error processing command: smashmatch FNF. Please try again.")
            return None

    def produce_log_proba(self, x, il=None, nr=5, no_details=True, force=False, quantize=False):
        '''
        Predicts logarithmic probability for the input time series to classify as any of the possible classes fitted

        Inputs -
            x (numpy.nda or pandas.DataFrame): input data (each row is a
                different timeseries)
            il (int): length of the input timeseries to use
            nr (int): number of times to run SmashMatch (for refining results)
            no_details (boolean): do not print SmashMatch cpu usage/speed of
                algorithm while running clasification
            force (boolean): force re-classification on current dataset
            quantize (boolean): if input timeseries have not been quantized,
                apply class quantizer to input timeseries

        Outputs -
            np.nda of shape n x m if successful or None if not successful
                where n = number of timeseries and m = number of classes
                probabilities are listed in an order corresponding to the classes attribute
        '''
        probs = self.produce_proba(x, il, nr, no_details, force, quantize)
        if probs is not None:
            return np.log(probs)
        else:
            return None

    def get_params(self):
        '''
        A noop
        '''
        return None

    def set_params(self):
        '''
        A noop
        '''
        return None


def cleanup():
    '''
    Maintenance function:
    Delete library/result files before closing the script; no I/O
    '''

    prev_wd = os.getcwd()
    os.chdir(CWD)
    if os.path.exists(CWD + "/" + PREFIX):
        command = "rm -r " + CWD + "/" + PREFIX
        sp.Popen(command, shell=True, stderr=sp.STDOUT).wait()
    os.chdir(prev_wd)


atexit.register(cleanup)


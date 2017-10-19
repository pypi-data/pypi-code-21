import os
import pdb
import uuid
import atexit
import sys
import subprocess as sp
import numpy as np
from numpy import nan
import pandas as pd
from sklearn import cluster
from datasmash.utils import write_series, preprocess_map, quantizer, condense
from datasmash.primitive_interfaces.clustering import ClusteringPrimitiveBase
from datasmash.config import CWD, TEMP_DIR, BIN_PATH, PREFIX


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


class SmashClustering(ClusteringPrimitiveBase):
    '''
    Object for running Data Smashing to calculate the distance matrix between n
        timeseries and using sklearn.cluster classes to cluster;
        inherits from UnsupervisedSeriesLearningBase API

    Inputs -
        bin_path(string): Path to Smash binary as a string
        quantiziation (function): quantization function for input timeseries
            data

    Attributes:
        bin_path (string): path to bin/smash
        quantizer (function): function to quantify input data
        num_dimensions (int): number of dimensions used for clustering

        (Note: bin_path and num_dimensions can be set by assignment,
        input and quantizer must be set using custom method)
    '''

    def __init__(self, bin_path=BIN_PATH, n_clus=8, cluster_class=None,
                 preproc=quantizer) -> None:
        self.__bin_path = os.path.abspath(bin_path)
        self.__smashmatch_bin_path = os.path.abspath(bin_path + 'smashmatch')
        self.__num_clusters = n_clus
        if cluster_class is None:
            self.__cluster_class = cluster.KMeans(n_clusters=self.__num_clusters)
        else:
            self.__cluster_class = cluster_class
        prev_wd = os.getcwd()
        os.chdir(CWD)
        sp.Popen("mkdir "+ TEMP_DIR, shell=True, stderr=sp.STDOUT).wait()
        self.__file_dir = CWD + "/" + TEMP_DIR
        os.chdir(prev_wd)
        self.__input_dm_fh = None
        self.__input_dm_fname = None
        self.__output_dm_fname = None
        self.__command = (self.__bin_path + "/smash")
        self.__input_e = None

        sp.Popen("mkdir "+ PREFIX, shell=True, stderr=sp.STDOUT).wait()
        self.__file_dir = CWD + "/" + PREFIX
        os.chdir(prev_wd)
        self.__classes = []
        self.__lib_files = [] # list of LibFile objects
        self.__lib_command = " -F "
        self.__smashmatch_command = self.__smashmatch_bin_path
        self.__input = None
        self.__mapper = {}
        self.__preproc = preproc

    def set_training_data(self, data) -> None:
        self._data = data
        self.__quantized_data = preprocess_map(self.__preproc, self._data)

    def _get_dm(self, first_run, max_len=None, num_get_dms=5, details=False):
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
            results = np.loadtxt(\
            fname=(self.__file_dir+"/"+self.__output_dm_fname), dtype=float)
            return results
        except IOError:
            print("Error: Smash calculation unsuccessful. Please try again.")

    def _fit(self, ml=None, nr=None, d=False, y=None, is_affinity=False):
        '''
        Uses Data Smashing to compute the distance matrix of the input time
        series and fit Data Smashing output to clustering class

        Inputs -
            ml (int): max length of data to use
            nr (int): number of runs of Smash to compute distance matrix
                (refines results)
            d (boolean): do (True) or do not (False) show cpu usage of Smash
                algorithm
            y (numpy.ndarray): labels for fit method of user-defined
                clustering_class

        Outuputs -
            (numpy.ndarray) distance matrix of the input timeseries
            (shape n_samples x n_samples)
        '''

        if self.__input_dm_fh is None:
            self._output = self._get_dm(True, ml, nr, d)
            self._output = self._output+self._output.T
            self.__cluster_class.fit(self._output)
            if is_affinity:
                self._output =np.reciprocal(self._output+1e-10)
            return self._output
        else:
            self._output = self._get_dm(False, ml, nr, d)
            self._output = self._output+self._output.T
            self.__cluster_class.fit(self._output)
            if is_affinity:
                self._output =np.reciprocal(self._output+1e-10)
            return self._output

    def fit(self, ml=None, nr=None, d=False, y=None, is_affinity=False):
        '''
        Returns output sklearn/clustering_class' fit_predict on distance matrix
        computed by Data Smashing algorithm and input y

        Inputs -
            ml (int): max length of data to use
            nr (int): number of runs of Smash to compute distance matrix
                (refines results)
            d (boolean): do (True) or do not (False) show cpu usage of Smash
                algorithm

        Returns -
            (np.ndarray) Computed cluster centers and predict cluster index
                from the input  using Data Smashing and sklearn cluster_class
        '''

        self.__input_e = self._fit(ml, nr, d,y=None,is_affinity=is_affinity)

        # we treat all examples (time series) that belong to the same cluster i
        # as a "library" in the form of a pandas DataFrame; the libraries must
        # be then mapped to their respective cluster label as a list of tuples 
        # in the form of [..., (library_i, i), ...]
        # e.g., [(lib0, 0), (lib1, 1), ...]
        mappings = []
        cluster_range = self.__cluster_class.n_clusters
        for i in range(cluster_range):
            # get all examples that belong to cluster label i
            X_in_cluster_i = self.__quantized_data[np.where(self.__cluster_class.labels_ == i)[0]]
            column_length = self.__quantized_data.shape[1]
            library = pd.DataFrame(X_in_cluster_i,
                                   columns=range(column_length),
                                   dtype=np.int32)
            mapping = (library, i)
            mappings.append(mapping)

        self.X, self.y = condense(mappings)

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

            self.__smashmatch_command += (input_name_command + self.__lib_command + "-T symbolic -D row ")
            self.__smashmatch_command += ("-L true true true -o " + TEMP_DIR + " -d false")
            self.__smashmatch_command += (" -n " + str(num_repeats))

            if input_length is not None:
                self.__smashmatch_command += input_length_command
            if no_details:
                self.__smashmatch_command += " -t 0"

            os.chdir(self.__file_dir)
            sp.Popen(self.__smashmatch_command, shell=True, stderr=sp.STDOUT).wait()
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
        self.__smashmatch_command = self.__smashmatch_bin_path
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
    def produce(self, x, il=None, nr=5, no_details=True, force=False):
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

    def get_params(self):
        pass

    def set_params(self):
        pass



def cleanup():
    '''
    Maintenance method:
    Clean up library files before closing the script; no I/O
    '''

    prev_wd = os.getcwd()
    os.chdir(CWD)
    if os.path.exists(CWD + "/" + TEMP_DIR):
        command = "rm -r " + CWD + "/" + TEMP_DIR
        sp.Popen(command, shell=True, stderr=sp.STDOUT).wait()
    os.chdir(prev_wd)


atexit.register(cleanup)

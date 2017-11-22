from sklearn import preprocessing
#import primitive
import sys
import os
#sys.path.append('corex_topic/')
from corextext.corextext.corex_topic import Corex
#import corex_topic.corex_topic as corex_text
from collections import defaultdict
from scipy import sparse
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import numpy as np

from primitive_interfaces.unsupervised_learning import UnsupervisedLearnerPrimitiveBase
from typing import NamedTuple, Union, Optional, Sequence


Input = pd.DataFrame
Output = np.ndarray
Params = NamedTuple('Params', [
    ('latent_factors', np.ndarray),  # Coordinates of cluster centers.
])


class TFIDF: #(Primitive):
    def __init__(self, replace_df = True, raw_data_path = None, **kwargs):
    	'''TO DO:  Add functionality to analyze multiple columns together'''
    	self.cls = 'corex_primitives.tfidf' 
    	#super().__init__(name = 'TFIDF', cls = 'corex_primitives.tfidf')

    	self.bow = TfidfVectorizer(decode_error='ignore', **kwargs)
    	
    	self.replace_df = True #necessary?
    	self.raw_data_path = raw_data_path


    def fit(self, X, y = None):
        self.columns = list(X)
        if len(self.columns) > 1:
            self.columns = self.columns[0] if self.columns[0] != X.index.name else self.columns[1]
            print ('WARNING: Only first column being analyzed', self.columns)
            # TO DO: handle multiple? naming in transform... modify read_text

        if self.raw_data_path is not None:
            #for col in self.columns: #multiple columns?
            self.idf_ = self.bow.fit_transform(self._read_text(X, self.columns, self.raw_data_path))
        else: #data frame contains raw text
			#for col in self.columns:
            self.idf_ = self.bow.fit_transform(X[col].values)
        return self

    def transform(self, X, y = None):
    	# just let X be new dataframe of single column
    	self.idf_df = pd.DataFrame(columns = str(self.columns+'_tfidf'), index = X.index) 
    	self.idf_df.fillna()
    	self.idf_df= self.idf_df.astype('object')
    	
    	for i, _ in self.idf_df.iterrows():
    		#for col in self.columns:
    		self.idf_df.loc[i, self.columns] = self.idf_[i, :]
    	
        # returns dataframe in order to put array rows in each index
    	return self.idf_df
    			
    	# returns matrix (n_samples, n_vocab) instead of a single pandas df
    	# return self.idf_

    def fit_transform(self, X, y = None):
    	#only set up for one column... last column will be stored / returned if multiple given
    	self.fit(X, y)
    	return self.transform(X, y)

    def _read_text(self, df, columns, data_path):
        column = columns # still takes column just in case want to switch back
        df = pd.DataFrame(df)
        #for col in columns:
        for i, _ in df.iterrows():
            file = df.loc[i, column]
            #legacy check for faulty one-hot encoding
            file = file if not isinstance(file, int) else str(file)+'.txt' 
            with open(os.path.join(data_path, file), 'r') as myfile:
                    yield myfile.read()

    def annotation(self):
        if self._annotation is not None:
            return self._annotation
        self._annotation = Primitive()
        self._annotation.name = 'TFIDF'
        self._annotation.task = 'FeatureExtraction'
        self._annotation.learning_type = 'NA'
        self._annotation.ml_algorithm = 'NA'
        self._annotation.tags = ['feature_extraction', 'text']
        return self._annotation

    def _get_feature_names(self):
    	return ['tfidf'] # col + '_' + 'tfidf' in L2 execution


class CorexText(UnsupervisedLearnerPrimitiveBase[Input, Output, Params]):  #(Primitive):
    """
    Learns latent factors / topics which explain the most multivariate information in bag of words representations of documents. Returns learned topic scores for each document. Also supports hierarchical models and 'anchoring' to encourage topics to concentrate around desired words.
    """
    __author__ = "Rob Brekelmans <brekelma@usc.edu>, Greg Ver Steeg"
    __metadata__ = {
        "team": "ISI DSBox",
        "common_name": "CorexText",
        "algorithm_type": ["DimensionalityReduction"],
        "compute_resources": {
            "sample_size": [0.000912, 1.869],
            "sample_unit": ["MB", "MB"],
            "disk_per_node": [1, 1],
            "expected_running_time": [14, 52],
            "gpus_per_node": [],
            "cores_per_node": [1, 1],
            "mem_per_gpu": [],
            "mem_per_node": [],
            "num_nodes": [],
        }
    }


    def __init__(self, n_hidden : int = 10, iterations: int = 200, max_df: float = 0.9, min_df: float = 2, max_features: int = None, 
        get_text : bool = False, data_path : str= None, count: str ='binarize', eps: float = 1e-5, seed : bool =None, verbose : bool =False,  **kwargs) -> None:

        super().__init__()

        self.n_hidden = n_hidden #DEFAULT = 10 topics (no latent_pct equivalent)
        self.max_iter = iterations
        self.max_df = max_df
        self.min_df = min_df #note: float = %, int = count of document frequencies
        self.max_features = max_features
        self.get_text = get_text
        self.data_path = data_path

        # no real need to pass extra Corex parameters.  kwargs used for TFIDF
        self.model = Corex(n_hidden= self.n_hidden, max_iter = self.max_iter, eps = eps, seed = seed, verbose= verbose, count = count)#, **kwargs)

        if not self.get_text:
            self.bow = TfidfVectorizer(input = 'content', decode_error='ignore', max_df = self.max_df, min_df = self.min_df, max_features = self.max_features, **kwargs)
        else:
            self.bow = TfidfVectorizer(input = 'filename', max_df = self.max_df, min_df = self.min_df, max_features = self.max_features, **kwargs)
        #if max_factors not None and n_hidden is None:
       #    self.n_hidden = int(max_factors/len(self.columns))
        #else:
         
    def fit(self, timeout : float = None, iterations : int = None) -> None: #X : Sequence[Input]): 
        #self.columns = list(X)
        #X_ = X[self.columns].values # useless if only desired columns are passed
        if self.fitted:
            return

        if not hasattr(self, 'training_inputs'):
            raise ValueError("Missing training data.")

        if iterations is not None:
            self.max_iter = iterations
            self.model.max_iter = self.max_iter

        bow = self.bow.fit_transform(self.training_inputs.values.ravel()) if not self.get_text else self.bow.fit_transform(self._get_raw_inputs())
        self.latent_factors = self.model.fit_transform(bow)
        self.fitted = True


    def produce(self, inputs : Sequence[Input], timeout : float = None, iterations : int = None) -> Sequence[Output]: # TAKES IN DF with index column
        #self.columns = list(X)
        #X_ = X[self.columns].values # useless if only desired columns are passed
        if iterations is not None:
            self.max_iter = iterations
            self.model.max_iter = self.max_iter

        if not self.fitted:
            bow = self.bow.fit_transform(inputs.values.ravel()) if not self.get_text else self.bow.fit_transform(self._get_raw_inputs(inputs = inputs))
            self.latent_factors = self.model.fit_transform(bow)
            self.fitted = True
        else:
            bow = self.bow.transform(inputs.values.ravel()) if not self.get_text else self.bow.transform(self._get_raw_inputs(inputs = inputs))
            self.latent_factors = self.model.transform(bow)

        return self.latent_factors

    def fit_transform(self, inputs : Sequence[Input], timeout : float = None, iterations : int = None) -> Sequence[Output]: # TAKES IN DF with index column
        #self.columns = list(X)
        #X_ = X[self.columns].values # useless if only desired columns are passed


        if iterations is not None:
            self.max_iter = iterations
            self.model.max_iter = self.max_iter

        bow = self.bow.fit_transform(inputs.values.ravel()) if not self.get_text else self.bow.fit_transform(self._get_raw_inputs(inputs = inputs))
        self.latent_factors = self.model.fit_transform(bow)
        self.fitted = True
        return self.latent_factors

    def _get_raw_inputs(self, inputs : Sequence[Input] = None) -> np.ndarray:
        raw_inputs = self.training_inputs.values if inputs is None else inputs.values
        inp = self.training_inputs.values if inputs is None else inputs.values
        if self.data_path is not None:
            for idx, val in np.ndenumerate(inp):
                raw_inputs[idx] = os.path.join(self.data_path, val)
        else:
            print('Warning: data_path not passed')
        
        return raw_inputs.ravel()
    

    def set_training_data(self, inputs : Sequence[Input]) -> None:
        self.training_inputs = inputs
        self.fitted = False

    def get_params(self) -> Params:
        return Params(latent_factors = self.latent_factors)

    def set_params(self, params: Params) -> None:
        self.latent_factors = params.latent_factors

    def annotation(self):
        if self._annotation is not None:
            return self._annotation
        self._annotation = Primitive()
        self._annotation.name = 'CorexText'
        self._annotation.task = 'FeatureExtraction'
        self._annotation.learning_type = 'UnsupervisedLearning'
        self._annotation.ml_algorithm = ['Dimension Reduction']
        self._annotation.tags = ['feature_extraction', 'text']
        return self._annotation

    def get_feature_names(self):
        return ['CorexText_'+ str(i) for i in range(self.n_hidden)]






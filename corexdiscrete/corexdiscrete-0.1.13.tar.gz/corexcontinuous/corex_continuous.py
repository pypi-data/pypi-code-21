from sklearn import preprocessing
#import primitive
import sys
import os
import corexcontinuous.linearcorex.linearcorex.linearcorex as corex_cont
#import LinearCorex.linearcorex as corex_cont
from collections import defaultdict
from scipy import sparse
import pandas as pd
import numpy as np


from primitive_interfaces.unsupervised_learning import UnsupervisedLearnerPrimitiveBase
from typing import NamedTuple, Union, Optional, Sequence


Input = pd.DataFrame
Output = np.ndarray
Params = NamedTuple('Params', [
    ('latent_factors', np.ndarray), 
])


class CorexContinuous(UnsupervisedLearnerPrimitiveBase):  #(Primitive):
    
    """
    Return components/latent factors that explain the most multivariate mutual information in the data under Linear Gaussian model. For comparison, PCA returns components explaining the most variance in the data.  Serves as DSBox 'wrapper' for https://github.com/gregversteeg/linearcorex"
    """
    __author__ = "Rob Brekelmans <brekelma@usc.edu>, Greg Ver Steeg"
    __metadata__ = {
        "team": "ISI DSBox",
        "common_name": "CorexContinuous",
        "algorithm_type": ["DimensionalityReduction"],
        "compute_resources": {
            "sample_size": [.3424],
            "sample_unit": ["MB"],
            "disk_per_node": [],
            "expected_running_time": [9],
            "gpus_per_node": [],
            "cores_per_node": [1],
            "mem_per_gpu": [],
            "mem_per_node": [],
            "num_nodes": [],
        }
    }

    def __init__(self, n_hidden : int = None, latent_pct : float = .2, max_iter : int = 10000, 
            tol : float = 1e-5, anneal : bool = True, discourage_overlap : bool = True, gaussianize : str = 'standard',  
            gpu : bool = False, verbose : bool = False, seed : int = None, **kwargs) -> None:
        
        super().__init__()

        self.kwargs = kwargs
        self.max_iter = max_iter
        self.tol = tol
        self.anneal = anneal
        self.discourage_overlap = discourage_overlap
        self.gaussianize = gaussianize
        self.gpu = gpu
        self.verbose = verbose
        self.seed = seed

        self.is_feature_selection = False
        self.hyperparameters = {'n_hidden': None, 'latent_pct': .2} # NOT TRUE, default = latent pct
        
        if n_hidden:
            self.n_hidden = n_hidden
            self.model = corex_cont.Corex(n_hidden= self.n_hidden, max_iter = max_iter, tol = tol, 
                anneal = anneal, discourage_overlap = discourage_overlap, gaussianize = gaussianize, 
                gpu = gpu, verbose = verbose, seed = seed, **kwargs)
        else:
            self.latent_pct = latent_pct
            self.model = None
            self.n_hidden = None

        # if latent_pct is not None and n_hidden is None:
        # 	self.n_hidden = int(len(self.columns)*latent_pct)
        # else:
        # 	self.n_hidden = 2 if n_hidden is None else n_hidden #DEFAULT = 2 

    def fit(self, timeout: float = None, iterations : int = None) -> None:
        if self.fitted:
            return
        if not hasattr(self, 'training_inputs'):
            raise ValueError("Missing training data.")

        self.fit_transform(self.training_inputs, timeout, iterations)
        self.fitted = True
        return self

    def produce(self, inputs : Sequence[Input], timeout : float = None, iterations : int = None) -> Sequence[Output]: 

        self.columns = list(inputs)
        X_ = inputs[self.columns].values 
    	
        if iterations is not None:
            self.max_iter = iterations

        if not self.fitted:
            if self.model is None and self.latent_pct:
                self.n_hidden = max(1, int(self.latent_pct*len(self.columns)))
                self.model = corex_cont.Corex(n_hidden= self.n_hidden, max_iter = self.max_iter, tol = self.tol, 
                    anneal = self.anneal, discourage_overlap = self.discourage_overlap, gaussianize = self.gaussianize, 
                    gpu = self.gpu, verbose = self.verbose, seed = self.seed, **self.kwargs)

            self.latent_factors = self.model.fit_transform(X_)
        else:
            self.latent_factors = self.model.transform(X_)

        return self.latent_factors

    def fit_transform(self, inputs : Sequence[Input], timeout: float = None, iterations : int = None) -> Sequence[Output]:
        
        self.columns = list(inputs)
        X_ = inputs[self.columns].values

        if self.n_hidden is None:
            self.n_hidden = max(1,int(self.latent_pct*len(self.columns)))

        if iterations is not None:
            self.max_iter = iterations


        if self.model is None and self.latent_pct:
        	self.model = corex_cont.Corex(n_hidden= self.n_hidden, max_iter = self.max_iter, tol = self.tol, 
                anneal = self.anneal, discourage_overlap = self.discourage_overlap, gaussianize = self.gaussianize, 
                gpu = self.gpu, verbose = self.verbose, seed = self.seed, **self.kwargs)

        self.latent_factors = self.model.fit_transform(X_)
        self.fitted = True
        return self.latent_factors

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
        self._annotation.name = 'CorexContinuous'
        self._annotation.task = 'FeatureExtraction'
        self._annotation.learning_type = 'UnsupervisedLearning'
        self._annotation.ml_algorithm = ['Dimension Reduction']
        self._annotation.tags = ['feature_extraction', 'continuous']
        return self._annotation

    def get_feature_names(self):
    	return ['CorexContinuous_'+ str(i) for i in range(self.n_hidden)]


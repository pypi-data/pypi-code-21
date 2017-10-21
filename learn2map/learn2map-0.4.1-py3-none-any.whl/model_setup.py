# -*- coding: utf-8 -*-
"""
Machine learning steps for processed data.

@author: Alan Xu
"""

from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble.base import _partition_estimators
from sklearn.ensemble.forest import _parallel_helper
from sklearn.externals import joblib


class RFbcRegressor(RandomForestRegressor):
    def __init__(self,
                 n_estimators=10,
                 max_depth=None,
                 min_samples_split=2,
                 max_features="auto",
                 oob_score=True,
                 n_jobs=1,
                 random_state=None,
                 verbose=0):
        super().__init__(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            max_features=max_features,
            oob_score=oob_score,
            n_jobs=n_jobs,
            random_state=random_state,
            verbose=verbose,
            warm_start=False)
        self.estimators1_ = []
        self.estimators2_ = []

    def fit(self, X, y=None, sample_weight=None):
        """
        fit rfbc model
        :param X:
        :param y:
        :return:
        """
        super().fit(X, y, sample_weight=None)
        self.estimators1_ = self.estimators_
        oob_y = self.oob_prediction_
        e1 = y - oob_y
        y2 = oob_y - e1
        super().fit(X, y2, sample_weight=None)
        self.estimators2_ = self.estimators_

    def predict(self, X):
        """
        predict rfbc model
        :param X:
        :return:
        """
        # Assign chunk of trees to jobs
        n_jobs, _, _ = _partition_estimators(self.n_estimators, self.n_jobs)

        # Parallel loop 1
        all_y_hat = joblib.Parallel(n_jobs=n_jobs, verbose=self.verbose,
                                    backend="threading")(
            joblib.delayed(_parallel_helper)(e, 'predict', X, check_input=False)
            for e in self.estimators1_)

        # Reduce
        y_hat1 = sum(all_y_hat) / len(self.estimators1_)

        # Parallel loop 2
        all_y_hat = joblib.Parallel(n_jobs=n_jobs, verbose=self.verbose,
                                    backend="threading")(
            joblib.delayed(_parallel_helper)(e, 'predict', X, check_input=False)
            for e in self.estimators2_)

        # Reduce
        y_hat2 = sum(all_y_hat) / len(self.estimators2_)

        # rfbc y_hat
        y_hat = y_hat1 * 2 - y_hat2

        return y_hat

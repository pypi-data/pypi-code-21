# -*- coding: utf-8 -*-
"""
Machine learning steps for processed data.

@author: Alan Xu
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestRegressor
# import forestci as fci
# from keras.models import Sequential
# from keras.layers import Dense
# from keras.wrappers.scikit_learn import KerasRegressor


class GridLearn(object):
    """
    Build machine learning object that can find the best parameters for final run.

    """

    def __init__(self, in_file='', y_column=None, mask_column=None):
        """
        :param in_file: input h5 file that contains the training data
        :param y_column: column index for response variable y
        :param mask_column: column index for mask (if exist, and should be after popping y_column)
        :param: best_params: param set that can be used in further learning
        """
        self.in_file = in_file
        if type(y_column) is list:
            self.y_column = y_column
        else:
            self.y_column = [y_column]
        if type(mask_column) is list:
            self.mask_column = mask_column
        else:
            self.mask_column = [mask_column]
        self.best_params = {}
        self.mdl = Pipeline([('scale', StandardScaler())])

    def tune_param_set(self, params, k=5):
        """
        Find the best param set that used in learning.
        :param k: number of folds used in cv
        :param params: parameter set used in grid search
        :return: best_params: param set that can be used in further learning
        :return: mdl: updated model using best_params
        """
        # train = pd.read_csv(self.in_file, sep=',', header=None)
        train = pd.read_hdf(self.in_file, 'df0')
        if self.y_column[0] is None:
            sys.exit('"y_column" must be defined in training process...')
        else:
            predictors = [x for x in train.columns if x not in self.y_column + self.mask_column]

        grid_search = GridSearchCV(self.mdl, params, n_jobs=-1, verbose=1, cv=k)
        grid_search.fit(train[predictors], train[self.y_column[0]])
        for p in grid_search.grid_scores_:
            print(p)
        print(grid_search.best_params_)
        print(grid_search.best_score_)
        self.best_params = grid_search.best_params_
        self.mdl.set_params(**self.best_params)
        return self.best_params, self.mdl

    def split_training(self, test_file, fraction=0.3):
        """
        :param fraction:
        :return:
        """
        train = pd.read_hdf(self.in_file, 'df0')
        if self.y_column[0] is None:
            sys.exit('"y_column" must be defined in training process...')
        else:
            predictors = [x for x in train.columns if x not in self.y_column + self.mask_column]
        self.mdl.fit(train[predictors], train[self.y_column[0]])
        preds = self.mdl.predict(test[predictors])
        label = test[self.y_column[0]]

    def predict_bigdata(self, test_file, out_file_h5):
        """
        sklearn prediction for big data
        :param out_file_h5:
        :param test_file:
        :return:
        """
        train = pd.read_hdf(self.in_file, 'df0')
        if self.y_column[0] is None:
            sys.exit('"y_column" must be defined in training process...')
        else:
            predictors = [x for x in train.columns if x not in self.y_column + self.mask_column]
        self.mdl.fit(train[predictors], train[self.y_column[0]])
        with pd.HDFStore(out_file_h5, mode='w') as store:
            for df in pd.read_hdf(test_file, 'df0', chunksize=500000):

                transX = self.mdl.named_steps['scale'].transform(df[predictors])
                y_hat = np.zeros([df[predictors].shape[0], self.mdl.named_steps['learn'].n_estimators])
                for i, pred in enumerate(self.mdl.named_steps['learn'].estimators_):
                    y_hat[:,i] = (pred.predict(transX))
                preds = np.nanmean(y_hat, axis=1)
                yerr = np.nanstd(y_hat, axis=1)

                # preds = self.mdl.predict(df[predictors])
                # # calculate inbag and unbiased variance
                # y_inbag = fci.calc_inbag(train[predictors].shape[0], self.mdl.named_steps['learn'])
                # y_V_IJ_unbiased = fci.random_forest_error(
                #     self.mdl.named_steps['learn'], y_inbag, train[predictors], df[predictors])
                # yerr = np.sqrt(y_V_IJ_unbiased)

                df1 = pd.Series(preds, name='Est')
                df2 = pd.Series(yerr, name='Err')
                df3 = df[['x', 'y']].reset_index(drop=True)
                df0 = pd.concat([df3, df1, df2], axis=1)
                store.append('df0', df0, index=False, data_columns=['Est'])
            store.create_table_index('df0', columns=['Est'], optlevel=9, kind='full')

    def setup_rf_model(self):
        """
        setup rf model
        :type rate: learning rate to specify
        :return: self.mdl
        """
        mdl1 = RandomForestRegressor(
            n_estimators=100,
            max_features="sqrt",
            min_samples_split=5,
            oob_score=True,
        )

        estimators = [
            ('scale', StandardScaler()),
            ('learn', mdl1)
        ]
        self.mdl = Pipeline(estimators)
        return self.mdl

    def setup_nn_model(self):
        """
        setup nn model
        :type rate: learning rate to specify
        :return: self.mdl
        """
        with pd.HDFStore(self.in_file, mode='r') as store:
            if self.y_column[0] is None:
                sys.exit('"y_column" must be defined in training process...')
            else:
                predictors = [x for x in store['df0'].columns if x not in self.y_column + self.mask_column]
        n_feature = len(predictors)

        model = Sequential()
        model.add(Dense(n_feature, input_dim=n_feature, init='normal', activation='relu'))
        model.add(Dense(1, init='normal'))
        model.compile(loss='mean_squared_error', optimizer='adam')
        mdl1 = KerasRegressor(
            build_fn=model,
            nb_epoch=100,
            batch_size=6,
            verbose=0,
        )
        estimators = [
            ('scale', StandardScaler()),
            ('learn', mdl1)
        ]
        self.mdl = Pipeline(estimators)
        return self.mdl

    # def setup_nn_model(self):
    #     """
    #     setup nn model
    #     :type rate: learning rate to specify
    #     :return: self.mdl
    #     """
    #     with pd.HDFStore(self.in_file, mode='r') as store:
    #         if self.y_column[0] is None:
    #             sys.exit('"y_column" must be defined in training process...')
    #         else:
    #             predictors = [x for x in store['df0'].columns if x not in self.y_column + self.mask_column]
    #     n_feature = len(predictors)
    #
    #     model = Sequential()
    #     model.add(Dense(n_feature, input_dim=n_feature, init='normal', activation='relu'))
    #     model.add(Dense(1, init='normal'))
    #     model.compile(loss='mean_squared_error', optimizer='adam')
    #     mdl1 = KerasRegressor(
    #         build_fn=model,
    #         nb_epoch=100,
    #         batch_size=6,
    #         verbose=0,
    #     )
    #     estimators = [
    #         ('scale', StandardScaler()),
    #         ('learn', mdl1)
    #     ]
    #     self.mdl = Pipeline(estimators)
    #     return self.mdl

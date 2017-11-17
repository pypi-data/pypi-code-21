#! python
# -*- coding: utf-8 -*-
# *****************************************************
# * FinX is a set of tools for Financial Data Science *
# * Copyright (C) 2017  Fite Analytics LLC            *
# *****************************************************
#
# This file is part of FinX.
#
#     FinX is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     FinX is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with FinX.  If not, see <http://www.gnu.org/licenses/>.
import tensorflow as tf
import pandas as pd
import tempfile
import random

def reset_vars(sess):
    sess.run(tf.global_variables_initializer())
    return sess


def reset_tf(sess):
    sess = None
    if sess:
        sess.close()
    tf.reset_default_graph()
    sess = tf.Session()
    return sess


def input_fn(df, num_epochs, num_threads, shuffle, predict):
    if predict is False:
        return tf.estimator.inputs.pandas_input_fn(x=pd.DataFrame({k: df[k].values for k in df.columns}),
                                               y=pd.Series(df[df.columns[-1]].values),
                                               num_epochs=num_epochs,
                                               num_threads=num_threads,
                                               shuffle=shuffle)
    else:
        return tf.estimator.inputs.pandas_input_fn(x=pd.DataFrame({k: df[k].values for k in df.columns[:-1]}),
                                               num_epochs=num_epochs,
                                               num_threads=num_threads,
                                               shuffle=shuffle)

def dnn_classifier(train, test, hidden_units, model_dir=None, predict=False, feature_columns=None,
                   n_classes=None, optimizer='Adagrad', activation_fn=tf.nn.relu, dropout=None, config=None,
                   num_epochs_train=None, num_epochs_test=1, num_threads=1, shuffle_train=True, shuffle_test=False, steps=2000):
    sess = None
    sess = reset_tf(sess)
    sess = reset_vars(sess)
    if model_dir is None:
        model_dir = tempfile.mkdtemp()
    columns = list(map(str, list(train.columns)))
    train.columns = columns

    if feature_columns is None:
        feature_columns = [tf.feature_column.numeric_column(str(col)) if col in train._get_numeric_data() else
                       tf.feature_column.categorical_column_with_hash_bucket(col, hash_bucket_size=len(
                           train[col].unique())) for col in train.columns[:-1]]
    if n_classes is None:
        n_classes = len(train[train.columns[-1]].unique())

    classifier = tf.estimator.DNNClassifier(hidden_units,
                                            feature_columns,
                                            model_dir=model_dir,
                                            n_classes=n_classes,
                                            optimizer=optimizer,
                                            activation_fn=activation_fn,
                                            dropout=dropout,
                                            config=config)
    if predict is False:
        train_input = input_fn(train, num_epochs_train, num_threads, shuffle_train, predict)
        classifier.train(input_fn=train_input, steps=steps)

        test.columns = columns
        test_input = input_fn(test, num_epochs_test, num_threads, shuffle_test, predict)
        results = classifier.evaluate(input_fn=test_input)
    else:
        test.columns = columns[:-1]
        test[columns[-1]] = pd.DataFrame(
            [random.choice(train[columns[-1]].unique()) for i in range(len(train[columns[-1]].unique()))])
        predict_input = input_fn(test, num_epochs_test, num_threads, shuffle_test, predict)
        results = list(classifier.predict(input_fn=predict_input))
    return results, model_dir

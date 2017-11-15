#! python
"""
author: Dick Mule
purpose: Provide out of the box machine learning neural networks for finx users
"""
from urllib.request import urlopen
import tensorflow as tf
import pandas as pd
import numpy as np
import tempfile
import random
import time
import os


def reset_vars():
    sess.run(tf.global_variables_initializer())


def reset_tf():
    global sess
    sess = None
    if sess:
        sess.close()
    tf.reset_default_graph()
    sess = tf.Session()


def input_fn(df, num_epochs, num_threads, shuffle):
    return tf.estimator.inputs.pandas_input_fn(x=pd.DataFrame({k: df[k].values for k in df.columns}),
                                               y=pd.Series(df[df.columns[-1]].values),
                                               num_epochs=num_epochs,
                                               num_threads=num_threads,
                                               shuffle=shuffle)


def dnn_classifier(train,test,hidden_units,num_epochs_train=None,num_epochs_test=1,
                  num_threads=1,shuffle_train=True, shuffle_test=False,steps=2000):
    sess = None
    reset_tf()
    reset_vars()
    model_dir = tempfile.mkdtemp()
    columns = list(map(str, list(train.columns)))
    train.columns = columns
    test.columns = columns

    feature_columns = [tf.feature_column.numeric_column(str(col)) if col in train._get_numeric_data() else
                       tf.feature_column.categorical_column_with_hash_bucket(col, hash_bucket_size=len(
                                                                    train[col].unique())) for col in train.columns[:-1]]

    classifier = tf.estimator.DNNClassifier(model_dir=model_dir,
                                            feature_columns=feature_columns,
                                            n_classes=len(train[train.columns[-1]].unique()),
                                            hidden_units=hidden_units)

    train_input = input_fn(train, num_epochs_train, num_threads=num_threads, shuffle=shuffle_train)
    classifier.train(input_fn=train_input, steps=steps)

    test_input = input_fn(test, num_epochs_test, num_threads=num_threads, shuffle=shuffle_test)
    results = classifier.evaluate(input_fn=test_input)

    return results, classifier

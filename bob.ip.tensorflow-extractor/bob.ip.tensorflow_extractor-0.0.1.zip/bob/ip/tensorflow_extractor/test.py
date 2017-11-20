import bob.io.base
from bob.io.base.test_utils import datafile
import bob.ip.tensorflow_extractor
import tensorflow as tf

import pkg_resources
import numpy
numpy.random.seed(10)
import os

slim = tf.contrib.slim
from . import scratch_network


def test_output():

    # Loading MNIST model
    filename = os.path.join(pkg_resources.resource_filename(
        __name__, 'data'), 'model.ckp')
    inputs = tf.placeholder(tf.float32, shape=(None, 28, 28, 1))

    # Testing the last output
    graph = scratch_network(inputs)
    extractor = bob.ip.tensorflow_extractor.Extractor(filename, inputs, graph)

    data = numpy.random.rand(2, 28, 28, 1).astype("float32")
    output = extractor(data)
    assert extractor(data).shape == (2, 10)
    del extractor

    # Testing flatten
    inputs = tf.placeholder(tf.float32, shape=(None, 28, 28, 1))
    graph = scratch_network(inputs, end_point="flatten1")
    extractor = bob.ip.tensorflow_extractor.Extractor(filename, inputs, graph)

    data = numpy.random.rand(2, 28, 28, 1).astype("float32")
    output = extractor(data)
    assert output.shape == (2, 1690)
    del extractor


def test_facenet():
    from bob.ip.tensorflow_extractor import FaceNet
    extractor = FaceNet()
    data = numpy.random.rand(3, 160, 160).astype("uint8")
    output = extractor(data)
    assert output.size == 128, output.shape


"""
def test_output_from_meta():

    # Loading MNIST model
    filename = os.path.join( pkg_resources.resource_filename(__name__, 'data'), "model.ckp.meta")
    inputs = tf.placeholder(tf.float32, shape=(None, 28, 28, 1))

    # Testing the last output
    graph = scratch_network(inputs)
    extractor = bob.ip.tensorflow_extractor.Extractor(filename, inputs, graph)

    data = numpy.random.rand(2, 28, 28, 1).astype("float32")
    output = extractor(data)
    assert extractor(data).shape == (2, 10)
    del extractor

    # Testing flatten
    inputs = tf.placeholder(tf.float32, shape=(None, 28, 28, 1))
    graph = scratch_network(inputs, end_point="flatten1")
    extractor = bob.ip.tensorflow_extractor.Extractor(filename, inputs, graph)

    data = numpy.random.rand(2, 28, 28, 1).astype("float32")
    output = extractor(data)
    assert extractor(data).shape == (2, 1690)
    del extractor
"""

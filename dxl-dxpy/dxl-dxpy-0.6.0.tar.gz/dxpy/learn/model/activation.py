import tensorflow as tf


def get_activation(name):
    if name.lower() == 'relu':
        return tf.nn.relu
    elif name.lower() == 'elu':
        return tf.nn.elu
    raise ValueError("Unknown name of activation: {}.".format(name))

import numpy as np
import tensorflow as tf


def ensure_shape(input_tensor, shape=None, *, batch_size=None):
    """
    Reshpe input_tensor to given shape.
    """
    if isinstance(input_tensor, np.ndarray):
        return np.copy(input_tensor)
    with tf.name_scope('shape_ensure'):
        shape_input = input_tensor.shape.as_list()
        if shape is None:
            shape = shape_input
        if shape[0] is None:
            shape[0] = batch_size
        return tf.reshape(input_tensor, shape)

import tensorflow as tf
from ..utils.general import device_name
from .base import Model
from ..graph import Graph, NodeKeys


class MultiGPUSplitor(Model):
    """
    A Helper class to create
    """

    def __init__(self, name='gpu_splitor', nb_gpu=2):
        super().__init__(name, nb_gpu=nb_gpu)

    @classmethod
    def _default_config(cls):
        result = dict()
        result.update(super()._default_config())
        result.update({
            'lazy_create': True,
            'register_inputs': False,
            'register_outputs': False,
            'pure': True,
        })
        return result

    def _kernel(self, feeds):
        x = feeds['input']
        return self._slice_tensor_for_gpu(x)

    def _get_shape_split(self, shape):
        if isinstance(shape, tf.TensorShape):
            shape_gpu = shape.as_list()
        else:
            shape_gpu = list(shape)
        if shape_gpu[0] is None:
            raise TypeError("Batch size can not be None for MultiGPUSplitor.")
        shape_gpu[0] = shape_gpu[0] // self.param('nb_gpu')
        return shape_gpu

    def _slice_tensor_for_gpu(self, tensor_input):
        result = []
        shape_gpu = self._get_shape_split(tensor_input.shape,)
        with tf.name_scope(self._get_tensor_name(tensor_input.name)):
            for id_slice in range(self.param('nb_gpu')):
                with tf.device(device_name('gpu', id_slice)):
                    slice_start = [id_slice * shape_gpu[0]] + \
                        [0] * (len(shape_gpu) - 1)
                    result.append(tf.slice(tensor_input, slice_start,
                                           shape_gpu, name='part_{}'.format(id_slice)))
        if len(result) == 0:
            return [tensor_input]
        return result

    def _get_tensor_name(self, name):
        prefix, idt = name.split(':')
        idt = int(idt)
        if idt == 0:
            return prefix
        else:
            return '{}_{}'.format(prefix, idt)


class PlaceHolder(Graph):
    """
    Placeholder for graph. Note this placeholder can be used to construct logic
    graph, thus may not create in tensorflow.
    """

    def __init__(self, shape, dtype=None, name='placeholder'):
        dtype = self._unified_dtype(dtype)
        super().__init__(name, shape=shape, dtype=dtype)

    @classmethod
    def _default_config(cls):
        from dxpy.collections.dicts import combine_dicts
        return combine_dicts({'dtype': tf.float32}, super()._default_config())

    @staticmethod
    def _unified_dtype(dtype):
        if isinstance(dtype, type(tf.float32)):
            return dtype
        type_desc = {
            tf.float32: ['FLOAT', 'FLOAT32', 'TF.FLOAT32'],
            tf.int64: ['INT', 'INT64', 'TF.INT64']
        }
        if isinstance(dtype, str):
            for k in type_desc:
                if dtype.upper() in type_desc[k]:
                    return k
            raise ValueError("Unknown dtype {}.".format(dtype))

    @property
    def shape(self):
        return self.param('shape')

    @property
    def dtype(self):
        return self.param('dtype')


class ShapeEnsurer(Model):
    """
    Used for assert on shapes or provide information for None dimensions.
    """

    def __init__(self, input_tensor, shape, name='shape_ensurer'):
        super().__init__(name, inputs={NodeKeys.INPUT: input_tensor},
                         shape=shape, simple_output=True)

    def _kernel(self, feeds):
        with tf.name_scope('shape_ensurer'):
            return tf.reshape(feeds[NodeKeys.INPUT], self.param('shape'))

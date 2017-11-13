import tensorflow as tf
from .base import Model, NodeKeys


def resize(inputs, size, method=None, name='upsampling'):
    if method is None:
        method = 'bilinear'
    input_shape = inputs.shape.as_list()
    h0, w0 = input_shape[1:3]
    h1 = int(h0 * size[0])
    w1 = int(w0 * size[1])
    with tf.name_scope(name):
        if method == 'nearest':
            h = tf.image.resize_nearest_neighbor(inputs, size=[h1, w1])
        elif method == 'bilinear':
            h = tf.image.resize_bilinear(inputs, size=[h1, w1])
    return h


def add_poisson_noise(input_tensor):
    if not isinstance(input_tensor, tf.Tensor):
        raise TypeError("Requre Tensor, got {}.".format(type(input_tensor)))
    with tf.name_scope('add_poisson_noise'):
        if input_tensor.dtype != tf.float32:
            input_tensor = tf.cast(input_tensor, tf.float32)
        return tf.random_poisson(input_tensor, [])


class DownSampler(Model):
    def __init__(self, input_tensor, ratio, method=None, padding=None, name='down_sampler', **config):
        super().__init__(name, inputs={NodeKeys.INPUT: input_tensor},
                         ratio=ratio, method=method, padding=padding, **config)

    @classmethod
    def _default_config(cls):
        from dxpy.collections.dicts import combine_dicts
        cfg = {
            'method': 'mean',
            'padding': 'same'
        }
        return combine_dicts(cfg, super()._default_config())

    def _kernel(self, feeds):
        x = feeds[NodeKeys.INPUT]
        if self.param('method') == 'mean':
            with tf.name_scope('down_sample'):
                x = tf.nn.avg_pool(x,
                                   [1] + list(self.param('ratio')) + [1],
                                   padding=self.param('padding').upper(),
                                   strides=[1] + list(self.param('ratio')) + [1])
        else:
            raise ValueError("Unsupported down sample method")
        return x


class MultiDownSampler(Model):
    """
    A helper model to create multiple down sampler and form their results to a dict.
    """

    def __init__(self, input_tensor, down_sample_ratios=None, keep_original=None, original_key=None, name='multi_down_sampler', **config):
        super().__init__(name,
                         inputs={NodeKeys.INPUT: input_tensor},
                         down_sample_ratios=down_sample_ratios,
                         keep_original=keep_original,
                         original_key=original_key, **config)

    @classmethod
    def _default_config(cls):
        from dxpy.collections.dicts import combine_dicts
        cfg = {
            'keep_original': True,
            'original_key': 'ds1x',
            'rigister_output_with_prefix': False
        }
        return combine_dicts(cfg, super()._default_config())

    def _kernel(self, feeds):
        image_orgin = feeds[NodeKeys.INPUT]
        result = dict()
        for n, v in self.param('down_sample_ratios').items():
            result[n] = DownSampler(image_orgin, v, name=self.name / n)()
        if self.param('keep_original'):
            result[self.param('original_key')] = self.tensor(NodeKeys.INPUT)
        return result


class Padder(Model):
    def __init__(self, input_tensor, padding=None, shape=None, name='padder', **config):
        super().__init__(name,
                         inputs={NodeKeys.INPUT: input_tensor},
                         padding=padding, shape=shape)

    def _kernel(self, feeds):
        x = feeds[NodeKeys.INPUT]

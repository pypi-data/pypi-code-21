import tensorflow as tf
import numpy as np
from .base import Model, NodeKeys

DENORM_INPUT_KEY = 'to_denorm'
DENORM_OUTPUT_KEY = 'denormed'


class Normalizer(Model):
    def __init__(self, name, inputs=None, **config):
        super().__init__(name, inputs, **config)

    @classmethod
    def _default_config(cls):
        from dxpy.collections.dicts import combine_dicts
        return combine_dicts({
            'add_denorm': False
        }, super()._default_config())

    def _pre_kernel_pre_inputs(self):
        from .tensor import PlaceHolder
        super()._pre_kernel_post_inputs()
        from dxpy.debug import dbgmsg
        dbgmsg(self.param('add_denorm'))
        dbgmsg(self.inputs)
        if self.param('add_denorm') and not DENORM_INPUT_KEY in self.inputs:
            self.inputs[DENORM_INPUT_KEY] = PlaceHolder(self.inputs[NodeKeys.INPUT].shape,
                                                        self.inputs[NodeKeys.INPUT].dtype,
                                                        name=DENORM_INPUT_KEY)

    def _kernel(self, feeds):
        with tf.name_scope('normalization'):
            result = self._normalization_kernel(feeds)
        if DENORM_INPUT_KEY in feeds:
            with tf.name_scope('denormalization'):
                denorm_feeds = dict()
                if isinstance(result, dict):
                    denorm_feeds.update(result)
                else:
                    denorm_feeds.update({NodeKeys.MAIN, result})
                denorm_feeds.update(feeds)
                result.update(self._denormalization_kernel(denorm_feeds))
        return result


class FixWhite(Normalizer):
    def __init__(self, name='normalizer/fix_white', inputs=None, **config):
        super().__init__(name, inputs, **config)

    def _normalization_kernel(self, feeds):
        return (feeds[NodeKeys.INPUT] - self.param('mean', feeds)) / self.param('std', feeds)

    def _denormalization_kernel(self, feeds):
        return feeds[NodeKeys.MAIN] * self.param('std', feeds) + self.param('mean', feeds)


class SelfMinMax(Normalizer):
    def __init__(self, name='normalizer/self_min_max', inputs=None, **config):
        super().__init__(name, inputs, **config)

    @classmethod
    def _default_config(cls):
        from dxpy.collections.dicts import combine_dicts
        return combine_dicts({
            'add_denorm': True
        }, super()._default_config())

    def _normalization_kernel(self, feeds):
        x = feeds[NodeKeys.INPUT]
        rmin = tf.reduce_min(x)
        rmax = tf.reduce_max(x)
        data = (x - rmin) / (rmax - rmin)
        return {'min': rmin, 'max': rmax, NodeKeys.MAIN: data}

    def _denormalization_kernel(self, feeds):
        return {DENORM_OUTPUT_KEY: feeds[DENORM_INPUT_KEY] * (feeds['max'] - feeds['min']) + feeds['min']}


class SelfMeanStd(Normalizer):
    def __init__(self, name='normalizer/self_mean_std', inputs=None, **config):
        super().__init__(name, inputs, **config)

    @classmethod
    def _default_config(cls):
        from dxpy.collections.dicts import combine_dicts
        return combine_dicts({
            'add_denorm': True
        }, super()._default_config())

    def _normalization_kernel(self, feeds):
        x = feeds[NodeKeys.INPUT]
        mean, stdv = tf.nn.moments(x)
        return {'mean': mean, 'std': stdv, NodeKeys.MAIN: (x - mean) / stdv}

    def _denormalization_kernel(self, feeds):
        return {DENORM_OUTPUT_KEY: feeds[DENORM_INPUT_KEY] * feeds['std'] + feeds['mean']}


class ReduceSum(Normalizer):
    """
    Normalize tensor to fix summation.
    """

    def __init__(self, name='normalizer/reduce_sum', inputs=None, fixed_sum=None, **config):
        super().__init__(name, inputs, fixed_sum=fixed_sum, **config)

    @classmethod
    def _default_config(cls):
        from dxpy.collections.dicts import combine_dicts
        return combine_dicts({
            'add_denorm': True
        }, super()._default_config())

    def _normalization_kernel(self, feeds):
        x = feeds[NodeKeys.INPUT]
        summation = tf.reduce_sum(x)
        return {'sum': summation,
                NodeKeys.MAIN: x / summation * self.param('fixed_sum', feeds)}

    def _denormalization_kernel(self, feeds):
        return {DENORM_OUTPUT_KEY: feeds[DENORM_INPUT_KEY] * feeds['sum'] / self.param('fixed_sum', feeds)}


def get_normalizer(name):
    if name.lower() in ['self_min_max', 'selfminmax']:
        return SelfMinMax
    if name == 'reduce_sum':
        return ReduceSum

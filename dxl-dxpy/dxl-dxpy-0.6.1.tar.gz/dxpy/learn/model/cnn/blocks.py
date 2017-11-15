import tensorflow as tf
from ..base import Model, NodeKeys
from ..activation import get_activation


class Conv2D(Model):
    def __init__(self, name='conv2d', input_tensor=None, kernel_size=None, strides=None, padding=None, activation=None, pre_activation=None, post_activation=None, **config):
        super().__init__(name, inputs={NodeKeys.INPUT: input_tensor}, kernel_size=kernel_size, strides=strides, padding=padding,
                         activation=activation, pre_activation=pre_activation, post_activation=post_activation, **config)

    @classmethod
    def _default_config(cls):
        from dxpy.collections.dicts import combine_dicts
        cfg = {
            'kernel_size': 3,
            'strides': (1, 1),
            'padding': 'same',
            'reuse': False,
            'activation': 'relu',
            'pre_activation': False,
            'post_activation': False,
            'kernel_name': 'conv2d'
        }
        return combine_dicts(cfg, super()._default_config())

    def _kernel(self, feeds):
        x = feeds[NodeKeys.INPUT]
        if self.param('pre_activation', feeds):
            with tf.name_scope('pre_activation'):
                x = get_activation(self.param('activation', feeds))(x)
        x = tf.layers.conv2d(x, self.param('filters', feeds),
                             self.param('kernel_size', feeds),
                             self.param('strides', feeds),
                             self.param('padding', feeds), name='conv')
        if self.param('post_activation', feeds):
            with tf.name_scope('post_activation'):
                x = get_activation(self.param('activation', feeds))(x)
        return x


class InceptionBlock(Model):
    def __init__(self, name='incept', input_tensor=None, **config):
        super().__init__(name, inputs={NodeKeys.INPUT: input_tensor}, **config)

    @classmethod
    def _default_config(cls):
        result = dict()
        result.update(super()._default_config())
        result.update({
            'paths': 3,
            'reuse': False,
            'pre_activation': True,
            'activation': 'relu'
        })
        return result

    def _kernel(self, feeds):
        x = feeds[NodeKeys.INPUT]
        filters = x.shape.as_list()[-1]
        if self.param('pre_activation', feeds):
            with tf.name_scope('pre_activation'):
                x = get_activation(self.param('activation', feeds))(x)
        paths = []
        for i_path in range(self.param('paths')):
            with tf.variable_scope('path_{}'.format(i_path)):
                h = Conv2D('conv2d_0', x,
                           filters=filters, kernel_size=1, pre_activation=True).as_tensor()
                for j in range(i_path):
                    h = Conv2D('conv2d_{}'.format(j + 1), h,
                               filters=filters, pre_activation=True).as_tensor()
                paths.append(h)
        with tf.name_scope('concat'):
            x = tf.concat(paths, axis=-1)
        x = Conv2D('conv_end', x, filters=filters).as_tensor()
        return x


class Residual(Model):
    def __init__(self, name, input_tensor, child_model=None, **config):
        if child_model is not None:
            child_models = {NodeKeys.CHILD_MODEL: child_model}
        else:
            child_models = None
        super().__init__(name,
                         inputs={NodeKeys.INPUT: input_tensor},
                         child_models=child_models,
                         **config)

    @classmethod
    def _default_config(cls):
        result = dict()
        result.update(super()._default_config())
        result.update({'ratio': 0.3})
        return result

    def _kernel(self, feeds):
        x = feeds[NodeKeys.INPUT]
        with tf.variable_scope('main_path'):
            y = self._child_models[NodeKeys.CHILD_MODEL](x)
        with tf.name_scope('add'):
            res = x + y * self.param('ratio', feeds)
        return res


class StackedConv2D(Model):
    def __init__(self, name, input_tensor, nb_stacked=None, activation=None, pre_activation=None, post_activation=None, **config):
        super().__init__(name, {NodeKeys.INPUT: input_tensor}, nb_stacked=nb_stacked,
                         activation=activation, pre_activation=pre_activation, post_activation=post_activation, **config)

    @classmethod
    def _default_config(cls):
        from dxpy.collections.dicts import combine_dicts
        cfg = {
            'activation': 'relu',
            'pre_activation': False,
            'post_activation': False,
            'filters': 32,
        }
        return combine_dicts(cfg, super()._default_config())

    def _pre_kernel_post_inputs(self):
        for i in range(self.param('nb_stacked')):
            if i == 0:
                pre_activation = self.param('pre_activation')
            else:
                pre_activation = False
            if i == self.param('nb_stacked') - 1:
                post_activation = self.param('post_activation')
            else:
                post_activation = True
            model = Conv2D('conv2d_{}'.format(i),
                           filters=self.param('filters'),
                           input_tensor=None,
                           activation=self.param('activation'),
                           pre_activation=pre_activation,
                           post_activation=post_activation,
                           lazy_create=True)
            self.register_child_model('conv2d_{}'.format(i), model)

    def _kernel(self, feeds):
        x = feeds[NodeKeys.INPUT]
        for i in range(self.param('nb_stacked')):
            x = self._child_models['conv2d_{}'.format(i)](x)
        return x

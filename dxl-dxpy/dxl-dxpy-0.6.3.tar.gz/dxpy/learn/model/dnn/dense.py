import tensorflow as tf
from ..base import Model


class StackDense(Model):
    def __init__(self, name, input_, filters):
        super().__init__(name, inputs={'input': input_}, filters=filters)

    def _kernel(self, feeds):
        x = feeds['input']
        for i, f in enumerate(self.param('filters')):
            if i < len(self.param('filters')) - 1:
                activ = tf.nn.relu
            else:
                activ = None
            x = tf.layers.dense(x, f, activation=activ)
        return x

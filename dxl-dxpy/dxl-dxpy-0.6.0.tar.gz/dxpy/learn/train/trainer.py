import tensorflow as tf

from ..graph import Graph
from ..scalar import ScalarVariable


class Trainer(Graph):
    def __init__(self, name, loss, variables=None, **config):
        """
        Inputs:
            loss: scalar or list of scalar (multi gpu)
            variables: list of tensors
        """
        super(__class__, self).__init__(name, **config)
        self.loss = loss
        if variables is None:
            variables = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES)
        self.variables = variables
        with tf.variable_scope(self.basename):
            self.register_node('learning_rate', ScalarVariable('learning_rate',
                                                               init_value=self.c['learning_rate']))
            self.optimizer = self._get_optimizer()
            self.register_main_node(self._get_train_step())
            self.register_main_task(self._train)
            self.register_task('multiply_learning_rate',
                               self._multiply_learning_rate)
            self.register_task('set_learning_rate', self._set_learning_rate)

    @classmethod
    def _default_config(cls):
        return {
            'is_multi_gpu': False,
            'learning_rate': 1e-3,
            'simple_mode': True,
        }

    def _train(self, feeds):
        sess = tf.get_default_session()
        sess.run(self.as_tensor(), feed_dict=feeds)

    def _multiply_learning_rate(self, feeds):
        old_value = self.nodes['learning_rate'].get_value()
        new_value = old_value * self.param('ratio', feeds)
        self.nodes['learning_rate'].set_value(new_value)

    def decay_learning_rate(self, ratio):
        self.run('multiply_learning_rate', feeds={'ratio': ratio})

    def _set_learning_rate(self, feeds):
        self.nodes['learning_rate'].set_value(self.param('learning_rate'),
                                              feeds)

    def _get_optimizer(self):
        return tf.train.AdamOptimizer(self.nodes['learning_rate'].as_tensor())

    def _get_gradients(self):
        from ..utils.general import device_name
        results = []
        if self.c.get('is_multi_gpu'):
            for i in range(self.c['nb_gpu']):
                with tf.device(device_name('gpu', i)):
                    results.append(self.optimizer.compute_gradients(
                        self.loss[i], self.variables))
        else:
            results.append(self.optimizer.compute_gradients(
                self.loss, self.variables))
        return results

    @classmethod
    def __analysis_grad_and_vars(cls, grad_and_vars):
        # Note that each grad_and_vars looks like the following:
                #   ((grad0_gpu0, var0_gpu0), ... , (grad0_gpuN, var0_gpuN))

                # for g, _ in grad_and_vars:
        nb_gpu = len(grad_and_vars)
        variables = grad_and_vars[0][1]
        grads = [g for g, _ in grad_and_vars if g is not None]
        if len(grads) > 0:
            grad = tf.add_n(grads) / nb_gpu
        else:
            grad = None

        #     # Add 0 dimension to the gradients to represent the tower.
        #     expanded_g = tf.expand_dims(g, 0)

        #     # Append on a 'tower' dimension which we will average over
        #     # below.
        #     grads.append(expanded_g)
        # # Average over the 'tower' dimension.
        # grad = tf.concat(axis=0, values=grads)
        # grad = tf.reduce_mean(grad, 0)
        # Keep in mind that the Variables are redundant because they are shared
        # across towers. So .. we will just return the first tower's pointer to
        # the Variable.
        return nb_gpu, grad, variables

    def __maybe_clip(self, grad):
        if self.c.get('with_clip', False):
            grad = tf.clip_by_value(grad,
                                    -self.c['clipv'],
                                    self.c['clipv'])
        return grad

    def _add_summary(self, average_grads):
        pass

    def _get_train_step_full(self):
        from ..scalar import global_step
        tower_gradients = self._get_gradients()
        with tf.name_scope('train_step'), tf.device('/cpu:0'):
            average_grads = []
            for grad_and_vars in zip(*tower_gradients):
                _, grad, var = self.__analysis_grad_and_vars(grad_and_vars)
                grad = self.__maybe_clip(grad)
                average_grads.append((grad, var))
            train_op = self.optimizer.apply_gradients(
                average_grads, global_step=global_step())
            self._add_summary(average_grads)
            return train_op

    def _get_train_step_simple(self):
        from ..scalar import global_step
        return self.optimizer.minimize(self.loss, global_step(), self.variables)

    def _get_train_step(self):
        """
        Inputs:
            tower_grads: *list or tuple* of grads
            optimizer: optimizer
        """
        if self.c.get('simple_mode'):
            return self._get_train_step_simple()
        else:
            return self._get_train_step_full()

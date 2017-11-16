import tensorflow as tf

from ..graph import Graph


class ScalarVariable(Graph):
    def __init__(self, name, **config):
        super(__class__, self).__init__(name, **config)
        with tf.variable_scope(self.basename, reuse=self.c.get('reuse')):
            self.create_variable_node(
                tf.float32, [], 'value', init_value=self.c.get('init_value'))
            self.create_placeholder_node(tf.float32, [], 'new_value')
            self.assign_op = self.nodes['value'].assign(
                self.nodes['new_value'])
        self.register_node('setter', self.assign_op)
        self.register_main_node(self.nodes['value'])
        self.register_task('set', self.set_value)

    def set_value(self, feeds):
        tf.get_default_session().run(self.assign_op, feed_dict={
            self.nodes['new_value']: feeds})

    def get_value(self):
        return tf.get_default_session().run(self.as_tensor())

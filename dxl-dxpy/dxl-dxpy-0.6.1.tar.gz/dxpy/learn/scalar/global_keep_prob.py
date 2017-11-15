import tensorflow as tf

from ..graph import Graph


def keep_prob():
    return graph().as_tensor()


def graph():
    if _instance is None:
        raise TypeError("Global keep prob not created yet.")
    return _instance


def get_value():
    return tf.get_default_session().run(keep_prob())


def set_value(value):
    graph().run('set', value)


_instance = None


class _KeepProb(Graph):
    def __init__(self, name):
        super(__class__, self).__init__(name)
        with tf.variable_scope('keep_prob'):
            self.create_variable_node(tf.float32, [], 'value', init_value=1.0)
            self.create_placeholder_node(tf.float32, [], 'new_value')
            self.assign_op = self.nodes['value'].assign(
                self.nodes['new_value'])
        self.register_node('setter', self.assign_op)
        self.register_main_node(self.nodes['value'])
        self.register_task('set', self.set_value)

    def set_value(self, feeds):
        tf.get_default_session().run(self.assign_op, feed_dict={
            self.nodes['new_value']: feeds})


def create():
    global _instance
    _instance = _KeepProb('keep_prob')

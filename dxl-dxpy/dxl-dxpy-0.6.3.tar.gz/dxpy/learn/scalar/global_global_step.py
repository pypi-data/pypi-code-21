import tensorflow as tf

from ..graph import Graph


def global_step():
    return graph().as_tensor()


def graph():
    if _instance is None:
        raise TypeError("Global step not created yet.")
    return _instance


def get_value():
    return tf.get_default_session().run(global_step())


def set_value(value):
    graph().run('set', value)


_instance = None


class _GlobalStep(Graph):
    def __init__(self, name='global_step'):
        super(__class__, self).__init__(name)
        self.register_main_node(tf.Variable(0, dtype=tf.int64, trainable=False,
                                            name='global_step'))
        with tf.name_scope('global_step_setter'):
            self.create_placeholder_node(tf.int64, [], 'new_value')
            self.assign_op = self.as_tensor().assign(self.nodes['new_value'])
        self.register_node('setter', self.assign_op)
        self.register_task('set', self.set_value)

    def set_value(self, feeds):
        tf.get_default_session().run(self.assign_op, feed_dict={
            self.nodes['new_value']: feeds})


def create():
    global _instance
    _instance = _GlobalStep()

from .base import Net


class GlobalStep(Net):
    def __init__(self, config):
        super(__class__, self).__init__(config)
        self.main = tf.Variable(
            0, dtype=tf.int32, trainable=False, name='global_step')

    def old(self):
        self.gs = tf.Variable(
            0, dtype=tf.int32, trainable=False, name='global_step')
        with tf.name_scope('global_step_setter'):
            self.__gs_value = tf.placeholder(dtype=tf.int32, name='gs_value')
            self.__gs_setter = self.gs.assign(self.__gs_value)
        self.add_node('global_step', tensor=self.gs, shape=[])

    def run(self, session, task=None, feeds=None):
        if task is None or task.upper() == "GET":
            return session.run(self.main)
        elif task.upper() == "SET":
            return session.run(self.__gs_setter, feed_dict={self.__gs_setter: feeds['global_step']})
        self.run_unknwn_task(session, task)

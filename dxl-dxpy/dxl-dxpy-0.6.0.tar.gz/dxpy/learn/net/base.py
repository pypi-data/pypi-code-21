import tensorflow as tf
from ..model import Model
from ..graph import Graph, NodeKeys


class Net(Model):
    """ Base class of nets.
    Net add some special tasks based on graph:
        1. train
        2. inference
        3. evaluate
        4. save/load
    """

    def __init__(self, name, inputs=None, **config):
        super().__init__(name, inputs, **config)

    @classmethod
    def _default_config(cls):
        from dxpy.collections.dicts import combine_dicts
        return combine_dicts({
            'add_trainer': True,
            'add_saver': True
        }, super()._default_config())

    def _tensors_need_summary(self):
        return dict()

    def _post_kernel_post_outputs(self):
        super()._post_kernel_post_outputs()
        from ..train import Trainer, Saver
        if self.param('add_trainer'):
            if NodeKeys.LOSS in self.nodes:
                self.register_node(NodeKeys.TRAINER,
                                   Trainer(self.name / 'trainer', self.nodes[NodeKeys.LOSS]))
        if self.param('add_saver'):
            self.register_node(NodeKeys.SAVER, Saver(self.name / 'saver'))

    def post_session_created(self):
        pass

    @property
    def session(self):
        return tf.get_default_session()

    def train(self, feeds=None):
        return self.nodes[NodeKeys.TRAINER](feeds)

    def inference(self, feeds=None):
        return self.session.run(self.tensor(NodeKeys.INFERENCE), self.get_feed_dict(feeds))

    def evaluate(self, feeds=None):
        return self.session.run(self.tensor(NodeKeys.EVALUATE), self.get_feed_dict(feeds))

    def save(self, feeds=None):
        return self.nodes[NodeKeys.SAVER].run('save', feeds)

    def load(self, feeds=None):
        return self.nodes[NodeKeys.SAVER].run('load', feeds)

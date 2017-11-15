import tensorflow as tf
from ..graph import Graph, NodeKeys
from contextlib import contextmanager


class Session(Graph):
    def __init__(self, name='session', **config):
        super().__init__(name, **config)
        self.__create_session()

    @classmethod
    def _default_config(cls):
        from dxpy.collections.dicts import combine_dicts
        return combine_dicts({
            'allow_growth': True,
            'log_device_placement': False
        }, super()._default_config())

    def __create_session(self):
        config = tf.ConfigProto()
        if self.param('allow_growth'):
            config.gpu_options.allow_growth = True
        if self.param('log_device_placement'):
            config.log_device_placement = True
        self.register_main_node(tf.Session(config=config))

    def run(self, tensors, feed_dict=None):
        with self.nodes[NodeKeys.MAIN].as_default():
            return self.nodes[NodeKeys.MAIN].run(tensors, feed_dict)

    def run_func(self, func):
        with self.nodes[NodeKeys.MAIN].as_default():
            return func()

    @contextmanager
    def as_default(self):
        with self.nodes[NodeKeys.MAIN].as_default():
            yield self.nodes[NodeKeys.MAIN]

    def post_session_created(self):
        self.as_tensor().run(tf.global_variables_initializer())
        # class SessionWithSupervisor(Graph):
        #     def __init__(self, name, **config):
        #         super(__class__, self).__init__(name, **config)

        #     def __construct(self):
        #         sv_para = {'summary_op': None}
        #         sms = self.c['save']['frequency']
        #         load_step = self.c['save']['load_step']
        #         if sms is not None:
        #             sv_para['save_model_secs'] = sms
        #         if load_step is not None:
        #             sv_para['init_fn'] = load_fn
        #         sv_para['saver'] = save_fn
        #         supervisor = tf.train.Supervisor(**sv_para)
        #         tf_config = tf.ConfigProto(
        #             log_device_placement=config.log.is_show_device_placement)
        #         tf_config.gpu_options.allow_growth = True
        #         sess = supervisor.prepare_or_wait_for_session(config=tf_config)
        #         return {'supervisor': supervisor, 'session': sess}

        #     def _load(self):
        #         pass
        # def supervisor(config, load_fn, save_fn):
        #     sv_para = {'summary_op': None}
        #     sms = config.save.frequency
        #     load_step = config.save.load_step
        #     if sms is not None:
        #         sv_para['save_model_secs'] = sms
        #     if load_step is not None:
        #         sv_para['init_fn'] = load_fn
        #     sv_para['saver'] = save_fn
        #     supervisor = tf.train.Supervisor(**sv_para)
        #     tf_config = tf.ConfigProto(
        #         log_device_placement=config.log.is_show_device_placement)
        #     tf_config.gpu_options.allow_growth = True
        #     sess = supervisor.prepare_or_wait_for_session(config=tf_config)
        #     return {'supervisor': supervisor, 'session': sess}

        # def _set_sesssv(self):
        #         from .supervisor import supervisor
        #         result = supervisor(self.params)

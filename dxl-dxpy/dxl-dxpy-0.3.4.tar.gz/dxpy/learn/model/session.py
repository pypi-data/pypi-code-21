    # def _set_sesssv(self):
    #     sv_para = {'summary_op': None}
    #     sms = self.params.get('save_model_secs')
    #     if sms is not None:
    #         sv_para['save_model_secs'] = sms
    #     if self.params['load_step'] is not None:
    #         sv_para['init_fn'] = self.load
    #     sv_para['saver'] = self.saver
    #     self.supervisor = tf.train.Supervisor(**sv_para)
    #     if self.params['is_show_device_placement']:
    #         config = tf.ConfigProto(log_device_placement=True)
    #     else:
    #         config = tf.ConfigProto()
    #     config.gpu_options.allow_growth = True
    #     self.sess = self.supervisor.prepare_or_wait_for_session(config=config)
    #     # self.saver = self.supervisor.saver
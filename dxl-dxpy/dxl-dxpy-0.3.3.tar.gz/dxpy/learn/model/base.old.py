""" Base class definition """
from collections import defaultdict
import pathlib
import tensorflow as tf
import os
import re
import numpy as np
from collections import ChainMap
from ..utils.general import with_config, ProgressTimer
from ..utils.prints import pp_json, pprint
from ..utils.options import Params
from tqdm import tqdm

from dxpy.collections.dicts import DXDict

# On restrict mode, tensors as allocated to CPU memory if not specified.
RESTRICT_MODE = True


class Net:
    """ Base class of nets.
    Which is used for:
        configs
        # TODO complete doc.
        # TODO deprecate device type, use auto inference by nb_gpus
    Level0:
        node: {node name: tensor}
        nodes_name_proxy: {node name: data name}
        hypers: {node name: values/ndarray}

        train_tasks: list of string, sub task names
        train_vars: {train sub task name: list of vars}
        losses: {train sub task name: tf.tensor}
        optimizers: {train sub task name: tf.train.xxxOptimizer}
        metrics: {train sub task name: tf.tensor}
        grads: {train sub task name: list/tuple of tf.tensors}
        train_steps: {train sub task name: tf.op}

    Level1:
        run_ops: { task names : *dict* of tf.ops to run }
        feed_dict: { task names : list of name of nodes to be feeded }

        run these tasks by calling run.
    Level2:
        datasets: {task name: dataset}
        data - net couple:
            data {name: np.ndarray}
            node {name: tf.tensor}
            nodes_name_proxy {name_in_node: name_in_data}
        task - run_op, feed_dict coutple:
            name: task name
            run_op {name: tf.tensors/tf.ops}
            feed_dict {name: node_names}
        lr - optimizer - train_step couple:
            loss {name: tf.tensor}
            optimizer {name: optimizer}
            train_step {name: tf.op}
    """

    def __init__(self, config):
        """
        Inputs:
            devices_type: 'auto' or 'gpus'. If 'gpus', losses and grads are lists, [0] cpu [1-n] gpus.
        """
        from . import train
        self.config = config

        # model external nodes
        self.nodes = DXDict()
        self.subnets = DXDict()

        # Variables and constants (stored in hypers)
        self.hypers = dict()

        #global step
        self.global_step = train.GlobalStep(config['train/global_step'])

        # keep prob
        self.kp, _ = self.add_node('keep_prob', shape=[])

        # training switch
        self.training, _ = self.add_node('training', shape=[], dtype=tf.bool)

        # learning rates
        if not isinstance(lr, dict):
            lr = {'main': lr}
        self.params['lr'] = lr
        self.lr = dict()

        for k in self.params['lr']:
            name = 'lr/' + k
            self.lr[k], _ = self.add_node(name, shape=[])
            self.hypers[name] = self.params['lr'][k]

        # train sub tasks
        self.train_tasks = ['main']
        self.train_vars = dict()
        self.losses = dict()
        self.grads = dict()
        self.metrices = dict()
        self.optimizers = dict()
        self.train_steps = dict()

        # Key by task
        self.summary_ops = dict()

        self.feed_dict = dict()
        self.feed_dict['default'] = list()
        for k in self.params['lr']:
            self.feed_dict['default'].append('lr/' + k)
        self.run_op = {
            'default': {'global_step': self.gs}
        }

        # Debug tensors
        self.debug_tensor = dict()

        # Key with 'train' and 'test'
        self.dataset = dict()

        # Session and managers
        self.sess = None
        self.saver = None
        self.summary_writer = None
        self.supervisor = None

        # Quick flags
        self.is_multi_gpu = self.p.nb_gpus > 1

    # Helper functions for constructing net:

    def add_node(self, name=None, tensor=None, is_gpu=False, dtype=None, shape=None, init_value=None, export_name=None):
        """ Add node for net. Nodes can be regard as API of Net.

        Rule:
            All tensors which is feedable need to be added
            Which implies all placeholders should be added via add_node.

            All outputs should be added to nodes.

        Inputs:
            name: node name, if is None, use tensor.name
            shape: node shape/tensor shape, if is `None`, use tensor.shape
            tensor: tensor to add to nodes. If is `None`, a placeholder will be created.
            is_multi_gpu: split tensor into multiple partial mini-batches.
        Returns:
            tensor: main part of tensor
            tensors_gpu: list of splited tensors
        Raises:
            ValueError
        """
        from . import tensor
        from .tensor import GPUTensorCreator
        tensor, tensors_gpu = GPUTensorCreator.create(
            tensor, name, shape, dtype, nb_gpu)
        self.nodes[name] = tensor
        if proxy_name is not None:
            self.nodes_name_proxy[name] = proxy_name
        return tensor, tensors_gpu

    @property
    def as_tensor(self):
        return self.main

    def __getitem__(self, name):
        from dxpy.filesystem.path import Path
        name = Path
        if name in self.nodes:
            return self.nodes[name]
        else:
            names = name.split('/')

            return self.nodes[names[0]]['/'.join(names[1:])]
        return None

    def run(self, feed_dict):
        pass

    def run_unknwn_task(self):
        pass

    def resolve_feed_dict(self):
        pass

    def init(self):
        pp_json(self.params, self.params['name'] + " PARAMS:")
        self._set_model()
        self._set_train()
        self._set_saver()
        self._set_sesssv()
        self._set_summary()
        self._set_task()
        pp_json(self.run_op, "RUN OPS:")
        pp_json(self.feed_dict, "FEED DICTS:")

    def _set_model(self):
        """ Construct model(s) for net.
        To construct:
            node: {node name: tensor}
            nodes_name_proxy: {node name: data name}

            losses: {sub task name: tf.tensor or list of tf.tensors}                    
        """
        pass

    def _set_task(self):
        """ Constrcut tasks for net.
        Tasks like train, evaluate, summary, predict, etc.
        To construct:
            run_op: { task names : *dict* of tf.ops to run }
            feed_dict: { task names : list of name of nodes to be feeded }
        """
        pass

    def _get_optimizer(self, sub_task_name):
        optim = self.optimizers.get(sub_task_name)
        if optim is None:
            name = self.p.optimizer_name.get(sub_task_name)
            if name in ['Adam', 'adam']:
                optim = tf.train.AdamOptimizer(self.lr[sub_task_name])
            elif name in ['RMSProp', 'rmsprop']:
                optim = tf.train.RMSPropOptimizer(self.lr[sub_task_name])
        return optim

    def _get_train_vars(self, sub_task_name):
        vars_list = self.train_vars.get(sub_task_name)
        return vars_list

    def _set_saver(self):
        # TODO: partial saver and loader.
        self.saver = tf.train.Saver()
        pass

    # def _set_sesssv(self):
    #     # sv_para = {'summary_op': None}
    #     # sms = self.params.get('save_model_secs')
    #     # if sms is not None:
    #     #     sv_para['save_model_secs'] = sms
    #     # if self.params['load_step'] is not None:
    #     #     sv_para['init_fn'] = self.load
    #     # sv_para['saver'] = self.saver
    #     # self.supervisor = tf.train.Supervisor(**sv_para)
    #     if self.params['is_show_device_placement']:
    #         config = tf.ConfigProto(log_device_placement=True)
    #     else:
    #         config = tf.ConfigProto()
    #     config.gpu_options.allow_growth = True
    #     self.sess = tf.Session(config=config)
    #     # self.saver = self.supervisor.saver

    def _set_summary(self):
        self.summary_writer = dict()
        for k in self.p.summary_modes:
            path_log = str(pathlib.Path(self.params['log_dir']) / k)
            self.summary_writer[k] = tf.summary.FileWriter(
                path_log, self.sess.graph)

        # Add summary service
        if self.params['summary_type'] == 'time':
            self.supervisor.loop(
                self.params['summary_freq'], self.summary_auto)

    # level-1 api
    def run(self, task, datas=None, verbose=0):
        """
        """
        run_ops = self.run_op[task]
        true_feed_dict = list(self.feed_dict['default'])
        true_feed_dict += self.feed_dict[task]
        if verbose >= 1:
            pp_json({'run_ops': run_ops, 'to_feed': true_feed_dict},
                    "RUN TASK: " + task)
        feed_dict = dict()
        for k in true_feed_dict:
            k_true = self.nodes_name_proxy.get(k, k)
            datas_all = ChainMap(datas, self.hypers)
            feed_dict[self.nodes[k]] = datas_all.get(k_true)
            if feed_dict[self.nodes[k]] is None:
                msg_format = r"Node: {0} with proxy name {1} was not found in hyers {2} and datas {3}"
                msg_content = (k, k_true, list(
                    self.hypers.keys()), list(datas.keys()))
                raise ValueError(msg_format.format(*msg_content))
        out = self.sess.run(run_ops, feed_dict=feed_dict)
        return out

    def partial_fit(self, data, sub_task=None, verbose=0):
        """ features are dict of mini batch numpy.ndarrays """
        task = 'train'
        if sub_task is not None:
            task = '{0}/{1}'.format(task, sub_task)
        true_data = dict()
        true_data['training'] = True
        true_data['keep_prob'] = self.p.keep_prob
        true_data.update(data)
        return self.run(task, true_data, verbose)

    def predict(self, data, sub_task=None, verbose=0):
        """ predict a mini-batch """
        task = 'predict'
        if sub_task is not None:
            task = '{0}/{1}'.format(task, sub_task)
        true_data = dict()
        true_data['training'] = False
        true_data['keep_prob'] = 1.0
        true_data.update(data)
        return self.run(task, true_data, verbose)

    def evaluate(self, data, sub_task=None, verbose=0):
        task = 'evaluate'
        if sub_task is not None:
            task = '{0}/{1}'.format(task, sub_task)
        true_data = dict()
        true_data['training'] = False
        true_data['keep_prob'] = 1.0
        true_data.update(data)
        return self.run(task, true_data, verbose)

    def dump(self, task, datas, save_name=None, verbose=0):
        result = self.run(task, datas, verbose)
        if save_name is None:
            save_name = 'dump%d' % (self.get_global_step())
        np.savez(save_name, **result)

    def summary(self, data, mode=None, sub_task=None, verbose=0):
        if mode is None:
            mode = 'train'
        task = 'summary'
        if sub_task is not None:
            task = '{0}/{1}'.format(task, sub_task)
        true_data = dict()
        true_data['training'] = False
        true_data['keep_prob'] = 1.0
        true_data.update(data)
        results = self.run(task, true_data, verbose)
        step = self.get_global_step()
        for k in self.run_op['summary'].keys():
            self.summary_writer[mode].add_summary(results[k], global_step=step)
        self.summary_writer[mode].flush()
        return results

    def set_dataset(self, name, dataset):
        self.dataset[name] = dataset

    # level-2 api
    def train_kernel(self, sub_task):
        ss = next(self.dataset[sub_task])
        res = self.partial_fit(ss, sub_task)
        msg = "LOSS=%6e, STEP=%5d" % (res['loss'], res['global_step'])
        return res, msg

    def set_dataset_auto(self, dataset_train, dataset_test):
        self.dataset['main'] = dataset_train
        self.dataset['train'] = dataset_train
        self.dataset['test'] = dataset_test

    def _train_sub_task_schadule(self, sub_task=None):
        if sub_task is None:
            sub_task = 'main'
        while True:
            yield sub_task

    def train(self, sub_task=None, steps=None, phase=1, decay=2.0, warmup=False):
        """ high level train.
        Inputs:
            sub_task: (Optional), if not None, run task train/sub_task
            steps: int or list of ints, steps per phase.
            phase: int. If steps is int, construct steps = [steps] * phase
            decay: learning rate decay per phase
            TODO: check warmup.
        """
        if not isinstance(steps, (list, tuple)):
            steps = [steps] * phase
        total_step = sum(steps)

        task_gen = self._train_sub_task_schadule(sub_task)

        if warmup:
            # warmup
            pt = ProgressTimer(total_step)
            cstep = 0
            lr_bak = self.p.lr['main']
            warming_up_phase = 10
            self.reset_lr(decay=2.0**warming_up_phase)
            pp_json(self.params, self.params['name'] + " PARAMS:")
            warmup_step = self.params['warmup_step']
            for i in range(warming_up_phase):
                for j in range(warmup_step):
                    _, msg = self.train_kernel(next(task_gen))
                    cstep += 1
                    pt.event(cstep, "[WARM]" + msg)
                self.reset_lr(decay=0.5)

        pt = ProgressTimer(total_step)
        cstep = 0
        for idx, sp in enumerate(steps):
            for i in range(sp):
                if warmup and warming_up > 0:
                    if warmup_step <= 0:

                        warming_up -= 1
                        warmup_step = warmup_step = self.params['warmup_step']
                    else:
                        warmup_step -= 1

                # if res['loss'] > 1e-2:
                #     self.dump(ss)
                cstep += 1
                _, msg = self.train_kernel(next(task_gen))
                pt.event(cstep, msg)
                if self.params['summary_type'] == 'step':
                    if i % self.params['summary_freq'] == 0 and i > 0:
                        self.summary_auto()
                if i % self.params['save_freq'] == 0 and i > 0:
                    self.save()

            # force save at end of each phase
            self.save()

            # decay lr at end of phase except the last one.
            if not idx == len(steps) - 1:
                self.reset_lr(decay=decay)

    def predict_auto(self, data, sub_task=None, batch_size=None, **kwargs):
        """ predict a large tensor, automatically seperate it into mini-batches. """
        nb_sample = None
        if batch_size is None:
            batch_size = self.p.batch_size
        for k in data.keys():
            if nb_sample is None:
                nb_sample = data[k].shape[0]
            else:
                if nb_sample != data[k].shape[0]:
                    raise ValueError("Wrong data shape.")
        nb_blocks = nb_sample // batch_size + 1
        preds = []
        pt = ProgressTimer(nb_blocks)
        for i in range(nb_blocks):
            skip = False
            data_block = dict()
            for k in data.keys():
                i_start = i * batch_size
                i_end = min([(i + 1) * batch_size, nb_sample])
                if i_start >= i_end:
                    skip = True
                    break
                data_block[k] = data[k][i_start:i_end, ...]
            if not skip:
                preds.append(self.predict(data_block))
            pt.event(i)
        results = dict()
        for k in preds[0].keys():
            results[k] = []
        for item in preds:
            results[k].append(item[k])
        for k in results.keys():
            results[k] = np.concatenate(results[k], 0)
        return results

    def summary_auto(self):
        result = dict()
        for k in self.summary_writer.keys():
            ss = self.dataset[k].sample()
            result[k] = self.summary(ss, mode=k)
        return result


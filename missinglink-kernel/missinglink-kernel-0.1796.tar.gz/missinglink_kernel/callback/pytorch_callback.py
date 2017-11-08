import copy
import logging

from .base_callback import BaseCallback, WEIGHTS_HASH_PREFIX
from .exceptions import MissingLinkException
from .interfaces import ModelHashInterface
from .settings import HyperParamTypes
from .state_counter import StateCounter


class PyTorchCallback(BaseCallback, ModelHashInterface):
    def __init__(self, owner_id, project_token, model, optimizer, stopped_callback=None, host=None):
        super(PyTorchCallback, self).__init__(owner_id, project_token, stopped_callback=stopped_callback,
                                              host=host, framework='pytorch')
        self.state_counter = StateCounter(self)
        self.model = model
        self.has_started = False
        self.latest_results = {}

        # monkey patch
        base_train = model.train
        base_zero_grad = optimizer.zero_grad
        base_step = optimizer.step

        # region define patched functions
        def patched_train():
            ret = base_train()
            self.begin_if_needed(optimizer)
            return ret

        def patched_zero_grad(epoch=None):
            if epoch is None:
                raise MissingLinkException('Epoch number is required to monitor batch')
            ret = base_zero_grad()
            self.before_run(optimizer, epoch)
            return ret

        def patched_step(*args, **kwargs):
            ret = base_step(*args, **kwargs)
            self.after_run(optimizer)
            return ret
        # endregion

        model.train = patched_train
        optimizer.zero_grad_batch = patched_zero_grad
        optimizer.step = patched_step

    def set_hyperparams(self, total_epochs=None, batch_size=None, epoch_size=None, **kwargs):
        super(PyTorchCallback, self).set_hyperparams(total_epochs=total_epochs, batch_size=batch_size,
                                                     epoch_size=epoch_size, **kwargs)

    def _get_structure_hash(self, net):
        layers = []
        for m in net.modules():
            layers.append(str(m))
        layers = tuple(layers)
        hash_string = self._hash(layers)
        return hash_string

    def get_weights_hash(self, net):
        from missinglink_kernel.callback.utilities.utils import hasharray, hashcombine

        hashes = list()
        for m in net.modules():
            layer_hashes = [hasharray(i.data.cpu().numpy()) for i in m.parameters()]
            hashes.extend(layer_hashes)

        hash_key = hashcombine(*hashes)
        return WEIGHTS_HASH_PREFIX + hash_key

    def wrap_metrics(self, metrics):
        """
        :param metrics: Single, list or dictionary of pytorch functionals
        """

        def wrap(base, key):
            def wrapped(*args, **kwargs):
                    ret = base(*args, **kwargs)
                    if hasattr(ret, 'data') and hasattr(ret.data, '__getitem__'):
                        self.latest_results[key] = ret.data[0]
                    else:
                        self.latest_results[key] = ret
                    return ret
            return wrapped

        if isinstance(metrics, dict):
            wrapped = copy.copy(metrics)

            for key in wrapped.keys():
                base = metrics[key]

                wrapped[key] = wrap(base, key)

        elif isinstance(metrics, (list, tuple)):
            wrapped = []

            for i in range(len(metrics)):
                base = metrics[i]

                wrapped.append(wrap(base, base.__name__))

        else:
            base = metrics

            wrapped = wrap(base, base.__name__)

        return wrapped

    def begin_if_needed(self, optimizer):
        if not self.has_started:
            self.hyperparams_from_optimizer(optimizer)
            structure_hash = self._get_structure_hash(self.model)
            self.train_begin({}, structure_hash=structure_hash)
            self.has_started = True

    def before_run(self, optimizer, epoch):
        self.begin_if_needed(optimizer)
        self.state_counter.begin_batch(epoch)
        self.latest_results = {}

    def after_run(self, optimizer):
        self.batch_end(self.state_counter.batch, self.state_counter.epoch, self.latest_results)

    def end_epoch(self, results, epoch):
        if not isinstance(results, dict):
            logging.warning("'results' param in end_epoch isn't a dictionary. it will be ignored")
            return

        metric_data = copy.copy(self.latest_results)
        for key, value in results.items():
            if not key.startswith('val_'):
                metric_data['val_' + key] = value
            else:
                metric_data[key] = value
        weights_hash = self.get_weights_hash(self.model)
        self.epoch_end(epoch, metric_data, weights_hash=weights_hash)
        self.state_counter.end_epoch(epoch)

    def end_train(self, **kwargs):
        self._train_end(metricData=self.latest_results, **kwargs)

    def hyperparams_from_optimizer(self, optimizer):
        optimizer_to_attrs = {
            'Adadelta': ['rho', 'eps', 'lr', 'weight_decay'],
            'Adagrad': ['lr', 'lr_decay', 'weight_decay'],
            'Adam': ['lr', 'beta_1', 'beta_2', 'eps', 'weight_decay'],
            'Adamax': ['lr', 'beta_1', 'beta_2', 'eps', 'weight_decay'],
            'ASGD': ['lr', 'lambd', 'alpha', 't0', 'weight_decay'],
            'LBFGS': ['lr', 'max_iter', 'max_eval', 'tolerance_grad', 'tolerance_change', 'history_size'],
            'RMSprop': ['lr', 'alpha', 'eps', 'weight_decay'],
            'Rprop': ['lr', 'etaminus', 'etaplus', 'minimum_step_size', 'maximum_step_size'],
            'SGD': ['lr', 'dampening', 'weight_decay'],
        }
        attr_to_hyperparam = {
            'lr': 'learning_rate',
            'lr_decay': 'learning_rate_decay',
            'eps': 'epsilon',
            'lambd': 'lambda',
            'max_iter': 'max_iteration',
            'max_eval': 'max_evaluation',
            'tolerance_grad': 'tolerance_gradient',
        }

        optimizer_type = optimizer.__class__.__name__
        params_groups = optimizer.param_groups

        if len(params_groups) < 1:
            return

        hyperparams = params_groups[0]

        expansions = {
            'betas': ['beta_1', 'beta_2'],
            'etas': ['etaminus', 'etaplus'],
            'step_sizes': ['minimum_step_size', 'minimum_step_size']
        }

        is_copied = [False]
        for name, names in expansions.items():
            values = hyperparams.get(name)
            if values is not None and len(values) == len(names):
                if not is_copied[0]:
                    hyperparams = copy.copy(hyperparams)
                    is_copied[0] = True

                for key, val in zip(names, values):
                    hyperparams[key] = val

        self.set_hyperparams(optimizer_algorithm=optimizer_type)
        self._extract_hyperparams(HyperParamTypes.OPTIMIZER, hyperparams, optimizer_to_attrs,
                                  attr_to_hyperparam, object_type=optimizer_type)

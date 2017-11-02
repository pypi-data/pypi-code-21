# coding=utf-8
from __future__ import absolute_import

import copy

from google.protobuf import json_format

from missinglink_kernel.callback.utilities.utils import hasharray, hashcombine
from .base_callback import BaseCallback, WEIGHTS_HASH_PREFIX
from .interfaces import ModelHashInterface
from .settings import MetricTypePrefixes
from .settings import HyperParamTypes
from .state_counter import StateCounter

base_init = None

# TODO: remove this
base_run = None


class TensorFlowCallback(BaseCallback, ModelHashInterface):
    """
    Callback for TensorFlow
    """

    def __init__(self, owner_id, project_token, total_epochs=None, stopped_callback=None, host=None):
        super(TensorFlowCallback, self).__init__(owner_id, project_token, stopped_callback=stopped_callback,
                                                 host=host, framework='tensorflow')
        global base_init, base_run
        self.state_counter = StateCounter(self)
        self.monitored_metrics = {}
        self.unmonitored_fetches_name = ''
        self.monitored_prediction = None
        self.monitored_truth = None
        self.latest_results = {}
        self.batches_queue = []
        self.total_epochs = total_epochs
        self._session = None

        if total_epochs:
            self.set_hyperparams(total_epochs=total_epochs)
            self.logger.warning(
                'total_epochs parameter in missinglink.TensorFlowCallback init is deprecated.\n'
                'Please use the set_hyperparams method instead.')

        # monkey patch
        import tensorflow as tf
        base_init = base_init or tf.Session.__init__
        base_run = base_run or tf.Session.run

        # region define patched functions
        def patched_init(_self, target='', graph=None, config=None):
            ret = base_init(_self, target, graph, config)
            self.begin(_self)
            self._session = _self
            return ret

        def run_wrapper(_self, fetches, feed_dict, options, run_metadata):
            all_monitored_metrics = copy.copy(self.monitored_metrics)

            custom_metrics_functions = {}

            for key in list(all_monitored_metrics):
                metric = all_monitored_metrics[key]
                if callable(metric):
                    custom_metrics_functions[key] = all_monitored_metrics.pop(key)

            total_fetches = all_monitored_metrics
            total_fetches[self.unmonitored_fetches_name] = fetches

            results = base_run(_self, total_fetches, feed_dict, options, run_metadata)

            custom_metrics = {}
            for key, metric_function in custom_metrics_functions.items():
                custom_metrics[MetricTypePrefixes.CUSTOM + key] = metric_function()

            results.update(custom_metrics)

            fetches_results = results.pop(self.unmonitored_fetches_name)

            return results, fetches_results

        def patched_run_batch(_self, fetches=None, feed_dict=None, options=None, run_metadata=None, epoch=None):
            if fetches is None:
                fetches = ()

            if epoch is None:
                self.logger.error('epoch value is needed to run batch. this run_batch call will not be monitored')
                return base_run(_self, fetches, feed_dict, options, run_metadata)

            if len(self.monitored_metrics) > 0:
                self.before_run(epoch)

                monitored_results, fetches_results = run_wrapper(_self, fetches, feed_dict, options, run_metadata)

                self.after_run(monitored_results)
                return fetches_results

            return base_run(_self, fetches, feed_dict, options, run_metadata)

        def patched_end_epoch(_self, fetches=None, feed_dict=None, options=None, run_metadata=None, epoch=None):
            def train_end_if_needed():
                if self.total_epochs and self.total_epochs == epoch + 1:  # deprecated, for backward compatibility
                    self.train_end()

                if HyperParamTypes.RUN in self.get_hyperparams():
                    current_total_epochs = self.get_hyperparams()[HyperParamTypes.RUN].get('total_epochs', 0)
                    if current_total_epochs == 0 or current_total_epochs == epoch + 1:
                        self.train_end()

            if fetches is None:
                fetches = ()

            if epoch is None:
                self.logger.error('epoch value is needed to run validation. this run_epoch call will not be monitored')
                return base_run(_self, fetches, feed_dict, options, run_metadata)

            if len(self.monitored_metrics) > 0:

                monitored_results, fetches_results = run_wrapper(_self, fetches, feed_dict, options, run_metadata)

                self.after_run(monitored_results, end_epoch=epoch)

                train_end_if_needed()

                return fetches_results

            result = base_run(_self, fetches, feed_dict, options, run_metadata)

            train_end_if_needed()

            return result

        def patched_run_test(_self, feed_dict=None, options=None, run_metadata=None):
            def generate_unique_key():
                while True:
                    tag = self.generate_tag()
                    if tag not in self.monitored_metrics:
                        return tag

            fetches = {k: v for k, v in copy.copy(self.monitored_metrics or {}).items() if not callable(v)}
            prediction_key = truth_key = None

            if self.monitored_prediction is not None:
                prediction_key = generate_unique_key()
                fetches[prediction_key] = self.monitored_prediction

            if self.monitored_truth is not None:
                truth_key = generate_unique_key()
                fetches[truth_key] = self.monitored_truth

            if len(fetches) > 0:
                monitored_results, fetches_results = run_wrapper(_self, fetches, feed_dict, options, run_metadata)

                prediction = truth = None
                if prediction_key:
                    prediction = fetches_results.pop(prediction_key)

                if truth_key:
                    truth = fetches_results.pop(truth_key)
            else:
                self.logger.warning(
                    'metrics, prediction and truth fetches are not set in missinglink callback,\n'
                    'test data will be ignored.\n'
                    'set them using the set_monitored_fetches() method')
        # endregion

        tf.Session.__init__ = patched_init
        tf.Session.run_batch = patched_run_batch
        tf.Session.end_epoch = patched_end_epoch

    def set_monitored_fetches(self, metrics=None, prediction=None, truth=None):
        """
        :param metrics: Single, list or dictionary of tensorflow fetches to monitor
        :param prediction: TensorFlow fetch of model's outputs
        :param truth: Tensorflow Placeholder for ground truths
        """
        if metrics is not None:
            if isinstance(metrics, dict):
                self.monitored_metrics = metrics
            elif isinstance(metrics, (list, tuple)):
                self.monitored_metrics = {fetch.name: fetch for fetch in metrics}
            else:
                self.monitored_metrics = {metrics.name: metrics}

            while True:
                name = self.generate_tag()
                if name not in self.monitored_metrics.keys():
                    self.unmonitored_fetches_name = name
                    break

        if prediction is not None:
            self.monitored_prediction = prediction

        if truth is not None:
            if self.monitored_prediction is not None:
                if self.monitored_prediction.get_shape().as_list() == truth.get_shape().as_list():
                    self.monitored_truth = truth
                else:
                    self.logger.warning(
                        'truth and prediction fetches of different shapes '
                        'given in set_monitored_fetches() is not allowed and will be ignored.\n'
                        'truth must be a placeholder for the correct prediction values')
            else:
                self.monitored_truth = truth

    def set_optimizer(self, optimizer):
        optimizer_to_attrs = {
            'AdadeltaOptimizer': ['_lr', '_rho', '_epsilon'],
            'AdagradOptimizer': ['_learning_rate', '_initial_accumulator_value'],
            'AdagradDAOptimizer': ['_learning_rate', '_initial_gradient_squared_accumulator_value',
                                   '_l1_regularization_strength', '_l2_regularization_strength'],
            'AdamOptimizer': ['_lr', '_beta1', '_beta2', '_epsilon'],
            'FtrlOptimizer': ['_learning_rate', '_learning_rate_power', '_initial_accumulator_value',
                              '_l1_regularization_strength', '_l2_regularization_strength'],
            'GradientDescentOptimizer': ['_learning_rate'],
            'MomentumOptimizer': ['_learning_rate', '_momentum', '_use_nesterov'],
            'ProximalAdagradOptimizer': ['_learning_rate', '_initial_accumulator_value',
                                         '_l1_regularization_strength', '_l2_regularization_strength'],
            'ProximalGradientDescentOptimizer': ['_learning_rate', '_l1_regularization_strength',
                                                 '_l2_regularization_strength'],
            'RMSPropOptimizer': ['_learning_rate', '_decay', '_momentum', '_epsilon']
        }
        attr_to_hyperparams = {
            '_lr': 'learning_rate',
            '_decay': 'learning_rate_decay'
        }

        for attrs in optimizer_to_attrs.values():
            for attr in attrs:
                if attr not in attr_to_hyperparams and attr.startswith('_'):
                    hyperparam = attr[1:]
                    attr_to_hyperparams[attr] = hyperparam

        self.set_hyperparams(optimizer_algorithm=optimizer.get_name())
        self._extract_hyperparams(HyperParamTypes.OPTIMIZER, optimizer, optimizer_to_attrs, attr_to_hyperparams)

    @classmethod
    def variable_to_value(cls, variable):
        import tensorflow as tf

        if isinstance(variable, tf.Tensor):
            variable = getattr(variable, "name")
        return variable

    def begin(self, session):
        structure_hash = self._get_structure_hash(session.graph_def)
        self.train_begin({}, structure_hash=structure_hash)

    def before_run(self, epoch):
        self.state_counter.begin_batch(epoch)

    def after_run(self, monitored_results, end_epoch=None):
        if end_epoch is not None:
            weights_hash = self.get_weights_hash(self._session.graph_def)
            metric_data = copy.copy(self.latest_results)
            for key, value in monitored_results.items():
                if not key.startswith('val_'):
                    metric_data['val_' + key] = value
                else:
                    metric_data[key] = value

            self.epoch_end(end_epoch, metric_data, weights_hash=weights_hash)
            self.state_counter.end_epoch(end_epoch)
        else:
            self.latest_results = monitored_results
            self.batch_end(self.state_counter.batch, self.state_counter.epoch, monitored_results)

    @classmethod
    def calculate_weights_hash(cls, session):
        weights = cls._get_weights(session)

        weights_hashes = []
        for weight in weights:
            weight_hash = hasharray(weight)
            weights_hashes.append(weight_hash)

        hash_key = hashcombine(*weights_hashes)
        return WEIGHTS_HASH_PREFIX + hash_key

    @classmethod
    def _get_weights(cls, session):
        import tensorflow as tf

        all_variables = tf.global_variables()
        return session.run(all_variables)

    # region ModelHashInterface

    def get_weights_hash(self, net):
        return self.calculate_weights_hash(self._session)

    def _get_structure_hash(self, net):
        # model here is session.graph_def
        model = json_format.MessageToDict(net)
        hash_string = self._hash(str(model))
        return hash_string

    # endregion

# coding=utf-8
from __future__ import absolute_import

import copy
import logging
import numpy as np
from collections import defaultdict
from contextlib import contextmanager

from six import string_types

from missinglink_kernel.callback.utilities.utils import hasharray, hashcombine, hash_value
from .base_callback import BaseCallback, WEIGHTS_HASH_PREFIX
from .exceptions import MissingLinkException
from .interfaces import ModelHashInterface, GradCAMInterface, ImageDimOrdering, VisualBackPropInterface
from .settings import HyperParamTypes, MetricPhasePrefixes, MetricTypePrefixes, AlgorithmTypes


class TensorFlowProject(BaseCallback):
    """A class for communicating with MissingLinkAI backend.

    A TensorFlowProject instance corresponds to a project created in the backend. This instance
    is used to create new experiments and send the data to the backend.
    """

    def __init__(self, owner_id, project_token, host=None):
        """Construct an new instance.

        # Arguments:
            owner_id: The owner's ID which can be obtained from the web dashboard
            project_token: The project's token which can be obtained from the web dashboard
            host: (Optional.) The backend endpoint
        """
        try:
            import tensorflow as tf
        except ImportError:
            raise MissingLinkException('Please install TensorFlow library')

        super(self.__class__, self).__init__(owner_id, project_token, host=host, framework='tensorflow')

    @contextmanager
    def create_experiment(self,
                          display_name=None,
                          description=None,
                          class_mapping=None,
                          optimizer=None,
                          hyperparams=None,
                          monitored_metrics=None,
                          custom_metrics=None):
        """Create an experiment context.

        This context defines a new experiment and allows the SDK to monitor the progress of the experiment.

        ```python
            # Setup the model

            # Add the optimizer op
            optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.1)
            train_op = optimizer.minimize(loss)

            project = TensorFlowProject(owner_id='owner_id', project_token='project_token')

            with project.create_experiment(
                display_name='MNIST multilayer perception',
                description='Two fully connected hidden layers',
                class_mapping={0: 'zero', 1: 'one', 2: 'two'},
                optimizer=optimizer,
                hyperparams={'batch_size': 100},
                monitored_metrics={'loss': loss},
                custom_metrics={'custom_loss': custom_loss_func}) as experiment:

                # Run the training loop
        ```

        # Arguments:
            display_name: (Optional.) The display name of the experiment
            description: (Optional.) The description of the experiment
            class_mapping: (Optional.) The class mapping of the experiment
            optimizer: (Optional.) The optimizer used to train the model. This should be an instance of
                `tf.Optimizer` or its subclasses.
            hyperparams: (Optional.) A dictionary of hyper-parameters whose keys are the parameter names. The
                values are the parameter's values.
            monitored_metrics: (Optional.) A dictionary whose values are tensors representing metrics to be monitored.
                The keys should be the metric names which are used to display on the web dashboard.
            custom_metrics: (Optional.) A dictionary whose values are metric functions. These functions take
                no input parameters and return a numeric value that needs to be monitored. The keys should be
                the metrics names which are used to display on the web dashboard.

        # Yields:
            An experiment context manager
        """
        self.set_properties(display_name=display_name, description=description, class_mapping=class_mapping)

        if optimizer is not None:
            self._set_optimizer(optimizer)

        if hyperparams is not None:
            self.set_hyperparams(**hyperparams)

        try:
            experiment = Experiment(self,
                                    monitored_metrics=monitored_metrics,
                                    custom_metrics=custom_metrics,
                                    logger=self.logger)
            experiment._context_validator.enter(Context.EXPERIMENT)

            yield experiment

            experiment._context_validator.exit(Context.EXPERIMENT)
        except Exception:
            self.logger.exception('Training has failed')
            raise

    @classmethod
    def variable_to_value(cls, variable):
        import tensorflow as tf

        if isinstance(variable, tf.Tensor):
            variable = getattr(variable, "name")

        return variable

    def _set_optimizer(self, optimizer):
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


_TF_PATCHED_RUN = {}


class Experiment(ModelHashInterface, GradCAMInterface, VisualBackPropInterface):
    """Context manager for an experiment."""

    @classmethod
    def __patch_run(cls, klasses, patch_method):
        for klass in klasses:
            _TF_PATCHED_RUN[klass] = klass.run
            klass.run = patch_method

    @classmethod
    def __unpatch_run(cls, klasses):
        for klass in klasses:
            if klass not in _TF_PATCHED_RUN:
                continue

            klass.run = _TF_PATCHED_RUN[klass]
            del _TF_PATCHED_RUN[klass]

    def __init__(self, project, monitored_metrics=None, custom_metrics=None, logger=None):
        """Create the context manager for an experiment.

        This context manager should be created by a TensorFlowProject instance. Please see
        `TensorFlowProject.create_experiment()` for details.
        """
        self.logger = logger or logging.getLogger(__name__)

        self._validate_monitored_fetches(monitored_metrics)
        self._validate_custom_metrics(custom_metrics)

        self.callback = project
        self._monitored_fetches = monitored_metrics or {}
        self._custom_metrics = custom_metrics or {}
        self._context_validator = ContextValidator(self.logger)
        self._max_iterations = None
        self._epoch_size = None
        self._has_started = False
        self._iteration = 0
        self._epochs = None
        self._epoch = 0
        self._train_session = None
        self._latest_metrics = {}
        self._validation_metrics = []
        self._is_iteration_with_validation = False  # is used to protect points with validation data
        self._properties = {}
        self._class_mapping = None

    def set_properties(self, **kwargs):
        self._class_mapping = kwargs.get("class_mapping")
        self._properties = kwargs

    def loop(self, max_iterations=None, condition=None, epoch_size=None):
        """Provides a training loop generator.

        This generator allows the MissingLinkAI SDK to correctly track each training iteration and its
        corresponding metrics.

        You would normally write the training loop as
        ```python
            for step in range(1000):
                # Perform a training step
        ```

        This can be converted to
        ```python
            for step in experiment.loop(max_iterations=1000):
                # Perform a training step
        ```

        If you wants to run the training steps while a condition is satisfied, a while loop is preferred.
        ```python
            threshold = 10
            step = 0
            while loss > threshold:
                # Perform a training step
                step += 1
        ```

        This can be converted to
        ```python
            threshold = 10
            for step in experiment.loop(condition=lambda _: loss > threshold):
                # Perform a training step
        ```

        If you want to collect and analyze metrics with respect to epochs, specify the `epoch_size` param with
        the number of iterations per epoch.

        # Arguments:
            max_iterations: The maximum number of training iterations to be run. Cannot be provided
                together with `condition`
            condition: The condition function to run the training steps. Once the condition fails, the
                training will terminate immediately. This function takes 1 parameter: a 0-based index
                indicating how many iterations have been run. Cannot be provided together with `max_iterations`.
            epoch_size: (Optional.) The number of iterations per epoch.

        # Yields:
            A 0-based index
        """
        if max_iterations and condition:
            raise MissingLinkException('Cannot provide both max_iteration and condition.')

        if not max_iterations and not condition:
            self.logger.error('Provide max_iteration or condition')
            raise MissingLinkException('Provide max_iteration or condition.')

        self._context_validator.enter(Context.LOOP)

        self._epoch_size = epoch_size
        self.callback.set_hyperparams(max_iterations=max_iterations, epoch_size=epoch_size,
                                      total_epochs=self._total_epochs(max_iterations, epoch_size))

        if max_iterations:
            self._max_iterations = max_iterations

            def condition(step):
                return step < max_iterations

        i = 0
        should_increment_epoch = True
        while condition(i):
            self._iteration += 1
            if should_increment_epoch:
                self._epoch += 1
                should_increment_epoch = False
            self._is_iteration_with_validation = False
            yield i

            weights_hash = None
            if self._is_iteration_with_validation or self._is_epoch_iteration:
                weights_hash = self.get_weights_hash(self._train_session)
            batch_weights_hash = None
            if self._is_iteration_with_validation:
                batch_weights_hash = weights_hash
            self.callback.batch_end(self._iteration, self._epoch, self._latest_metrics, iteration=self._iteration,
                                    is_test=self._is_iteration_with_validation, weights_hash=batch_weights_hash)
            if self._is_epoch_iteration:
                self.callback.epoch_end(self._epoch, self._latest_metrics, weights_hash=weights_hash)
                should_increment_epoch = True

            i += 1

        self.callback._train_end(iterations=self._iteration, metricData=self._latest_metrics)
        self._context_validator.exit(Context.LOOP)

    def epoch_loop(self, epochs):
        """Provides a epoch loop generator.

        This generator is used together with the `batch_loop` generator to run your training with
        epochs and batches using nested loops.

        You would normally write your training loops as
        ```python
        for epoch in range(epochs):
            for batch in range(batches):
                # Perform a training step on a batch of data
        ```

        This can be converted to
        ```python
        for epoch in experiment.epoch_loop(epochs):
            for batch in experiment.batch_loop(batches):
                # Perform a training step on a batch of data
        ```

        # Arguments:
            epochs: The total number of epochs
        # Yields:
            A 0-based index
        """
        self._context_validator.enter(Context.EPOCH_LOOP)

        self._epochs = epochs
        self.callback.set_hyperparams(total_epochs=epochs)

        for epoch in range(epochs):
            self._epoch += 1

            yield epoch

            weights_hash = self.get_weights_hash(self._train_session)
            batch_weights_hash = None
            if self._is_iteration_with_validation:
                batch_weights_hash = weights_hash
            self.callback.batch_end(self._iteration, self._epoch, self._latest_metrics,
                                    iteration=self._iteration, is_test=self._is_iteration_with_validation,
                                    weights_hash=batch_weights_hash)
            self.callback.epoch_end(self._epoch, self._latest_metrics, weights_hash=weights_hash)

        self.callback._train_end(iterations=self._iteration, metricData=self._latest_metrics)
        self._context_validator.exit(Context.EPOCH_LOOP)

    def batch_loop(self, batches):
        """Provides a batch loop generator.

        This generator should be nested in a `epoch_loop` generator. Please see `epoch_loop` for more details.

        # Arguments:
            batches: The total number of batches
        # Yields:
            A 0-based index
        """
        self._context_validator.enter(Context.BATCH_LOOP)

        self.callback.set_hyperparams(epoch_size=batches, max_iterations=self._epochs * batches)

        for batch in range(batches):
            self._is_iteration_with_validation = False
            self._iteration += 1

            yield batch

            if batch < batches - 1:
                # Last batch's batch_end will be call in `epoch_loop`
                weights_hash = None
                if self._is_iteration_with_validation:
                    weights_hash = self.get_weights_hash(self._train_session)
                self.callback.batch_end(self._iteration, self._epoch, self._latest_metrics,
                                        iteration=self._iteration, is_test=self._is_iteration_with_validation,
                                        weights_hash=weights_hash)

        self._context_validator.exit(Context.BATCH_LOOP)

    @contextmanager
    def train(self, monitored_metrics=None, custom_metrics=None):
        """Marks a training context.

        This context allows the SDK to patch the `tf.Session.run` and calculate training metrics if needed.
        As such, there must be only 1 `tf.Session.run` call within this context. Otherwise, the training
        iteration might be incorrectly incremented.

        The `monitored_metrics` and `custom_metrics` dicts will be merged with their corresponding values specified
        at the experiment level and the combined dict will be monitored as training metrics.

        # Arguments:
            monitored_metrics: (Optional.) A dictionary whose values are tensors representing metrics to be monitored.
                The keys should be the metric names which are used to display on the web dashboard.
            custom_metrics: (Optional.) A dictionary whose values are metric functions. These functions take
                no input parameters and return a numeric value that needs to be monitored. The keys should be
                the metrics names which are used to display on the web dashboard.

        # Yields:
            None
        """
        self._context_validator.enter(Context.TRAIN)

        self._validate_monitored_fetches(monitored_metrics)
        self._validate_custom_metrics(custom_metrics)

        monitored_fetches = monitored_metrics or {}
        monitored_fetches.update(self._monitored_fetches)
        custom_metrics = custom_metrics or {}
        custom_metrics.update(self._custom_metrics)

        self._patch_tf_session_for_train(monitored_fetches)
        yield
        if custom_metrics:
            custom_results = self._resolve_custom_metrics(custom_metrics, MetricPhasePrefixes.TRAIN)
            self._latest_metrics.update(custom_results)
        self._reset_tf_session()

        self._context_validator.exit(Context.TRAIN)

    def _on_test_begin(self, test_iter, model):
        weights_hash = self.get_weights_hash(model)
        self.callback._test_begin(test_iter, weights_hash)

    def _after_test_run(self, expected, predictions, probabilities):
        self.callback._test_iteration_end(expected, predictions, probabilities)

    @contextmanager
    def test(self, total_test_iterations=1, expected=None, predicted=None, monitored_metrics=None, custom_metrics=None):
        """
        Marks a test context.

        This context allows the SDK to patch the `tf.Session.run` and calculate test metrics if needed.

        The `monitored_metrics` and `custom_metrics` dicts will be merged with their corresponding values specified
        at the experiment level and the combined dict will be monitored as test metrics.

        :param total_test_iterations: Total iterations needed to go over test dataset
        :param predicted: a tensor for predictions
        :param expected: a tensor for expected values
        :param monitored_metrics: (Optional.) A dictionary whose values are tensors representing metrics to be monitored.
        :param custom_metrics: (Optional.) A dictionary whose values are metric functions.
        :return None
        """
        self._context_validator.enter(Context.TEST)

        self._validate_monitored_fetches(monitored_metrics)
        self._validate_custom_metrics(custom_metrics)

        monitored_fetches = monitored_metrics or {}
        if expected is not None and predicted is not None:
            monitored_fetches["expected"] = expected
            monitored_fetches["predicted"] = predicted

        monitored_fetches.update(self._monitored_fetches)
        custom_metrics = custom_metrics or {}
        custom_metrics.update(self._custom_metrics)

        self._on_test_begin(total_test_iterations, self._train_session)
        self._patch_tf_session_for_test(monitored_fetches)
        yield
        self._reset_tf_session()
        self._context_validator.exit(Context.TEST)

    @contextmanager
    def validation(self, monitored_metrics=None, custom_metrics=None):
        """Marks a validation context.

        This context allows the SDK to patch the `tf.Session.run` to calculate validation metrics.
        Unlike the `train` scope, you can include multiple runs e.g. by using a for-loop looping over a
        validation dataset by batches. The SDK will average out the validation metrics across these runs
        and collect the averaged value.

        The `monitored_metrics` and `custom_metrics` dicts will be merged with their corresponding values specified
        at the experiment level and the combined dict will be monitored as training metrics.

        # Arguments:
            monitored_metrics: (Optional.) A dictionary whose values are tensors representing metrics to be monitored.
                The keys should be the metric names which are used to display on the web dashboard.
            custom_metrics: (Optional.) A dictionary whose values are metric functions. These functions take
                no input parameters and return a numeric value that needs to be monitored. The keys should be
                the metrics names which are used to display on the web dashboard.

        # Yields:
            None
        """
        self._context_validator.enter(Context.VALIDATION)

        # Validate but do not throw exceptions so the experiment is not suddenly interrupted.
        self._validate_monitored_fetches(monitored_metrics, raise_exception=False)
        self._validate_custom_metrics(custom_metrics, raise_exception=False)

        monitored_fetches = monitored_metrics or {}
        monitored_fetches.update(self._monitored_fetches)
        custom_metrics = custom_metrics or {}
        custom_metrics.update(self._custom_metrics)

        self._patch_tf_session_for_validation(monitored_fetches)
        yield
        if custom_metrics:
            custom_results = self._resolve_custom_metrics(custom_metrics, MetricPhasePrefixes.VAL)
            self._latest_metrics.update(custom_results)
        self._on_validation_end()
        self._reset_tf_session()
        self._is_iteration_with_validation = True

        self._context_validator.exit(Context.VALIDATION)

    @property
    def _is_epoch_iteration(self):
        if self._epoch_size is None:
            return False

        return self._iteration % self._epoch_size == 0

    def _patch_tf_session_for_test(self, monitored_fetches):
        def patched_run(session, fetches, feed_dict=None, options=None, run_metadata=None):
            monitored_results, unmonitored_results = self._internal_session_run(
                monitored_fetches, session, fetches, feed_dict=feed_dict, options=options,
                run_metadata=run_metadata)

            if "expected" in monitored_results and "predicted" in monitored_results:
                expected, predicted = monitored_results["expected"], monitored_results["predicted"]
                predicted_classes = predicted.argmax(axis=-1)
                probabilities = predicted.max(axis=-1)

                expected = expected.tolist()
                predicted_classes = predicted_classes.tolist()
                probabilities = probabilities.tolist()
            else:
                expected = []
                predicted_classes = []
                probabilities = []

            self._after_test_run(expected, predicted_classes, probabilities)
            return unmonitored_results

        import tensorflow as tf
        self.__patch_run((tf.Session, tf.InteractiveSession), patched_run)

    def _patch_tf_session_for_validation(self, monitored_fetches):
        def patched_run(session, fetches, feed_dict=None, options=None, run_metadata=None):
            monitored_results, unmonitored_results = self._internal_session_run(
                monitored_fetches, session, fetches, feed_dict=feed_dict, options=options,
                run_metadata=run_metadata)
            validation_results = self._prefix_metric_data(monitored_results, MetricPhasePrefixes.VAL)

            self._validation_metrics.append(validation_results)
            return unmonitored_results

        import tensorflow as tf
        self.__patch_run((tf.Session, tf.InteractiveSession), patched_run)

    @classmethod
    def _prefix_metric_data(cls, monitored_results, prefix):
        metric_data = {}
        for key, value in monitored_results.items():
            metric_data[prefix + key] = value

        return metric_data

    def _patch_tf_session_for_train(self, monitored_fetches):
        def patched_run(session, fetches, feed_dict=None, options=None, run_metadata=None):
            self._train_session = session
            self._before_train_run(session)
            monitored_results, unmonitored_results = self._internal_session_run(
                monitored_fetches, session, fetches, feed_dict=feed_dict, options=options,
                run_metadata=run_metadata)
            self._latest_metrics = self._prefix_metric_data(monitored_results, MetricPhasePrefixes.TRAIN)

            return unmonitored_results

        import tensorflow as tf
        self.__patch_run((tf.Session, tf.InteractiveSession), patched_run)

    def _internal_session_run(self, monitored_fetches, session, fetches, feed_dict=None, options=None,
                              run_metadata=None):
        all_fetches = copy.copy(monitored_fetches)

        key_for_unmonitored_fetches = self._generate_unique_key(all_fetches.keys())
        all_fetches[key_for_unmonitored_fetches] = fetches

        monitored_results = _TF_PATCHED_RUN[type(session)](session, all_fetches, feed_dict, options, run_metadata)
        unmonitored_results = monitored_results.pop(key_for_unmonitored_fetches)

        return monitored_results, unmonitored_results

    @staticmethod
    def _resolve_custom_metrics(custom_metrics, metric_phase_prefix):
        results = dict()
        for key, metrics_function in custom_metrics.items():
            results[metric_phase_prefix + MetricTypePrefixes.CUSTOM + key] = metrics_function()
        return results

    def _average_validation_metrics(self):
        result = defaultdict(float)
        total = len(self._validation_metrics)
        for el in self._validation_metrics:
            for k, v in el.items():
                result[k] += v
        result = {k: v * 1.0 / total for k, v in result.items()}
        return result

    def _on_validation_end(self):
        averaged = self._average_validation_metrics()
        self._latest_metrics.update(averaged)
        self.logger.debug('Added validation metrics on iteration %s. Metrics are %s', self._iteration,
                          self._latest_metrics)
        self._validation_metrics = []

    def _before_train_run(self, session):
        if not self._has_started:
            self._has_started = True
            structure_hash = self._get_structure_hash(session)
            self.callback.train_begin(structure_hash=structure_hash)

    @classmethod
    def _reset_tf_session(cls):
        import tensorflow as tf
        cls.__unpatch_run((tf.Session, tf.InteractiveSession))

    @staticmethod
    def _validate_fetches_dict(fetches_dict):
        if fetches_dict is None:
            return

        if not isinstance(fetches_dict, dict):
            raise ValueError('Fetches %s must be a dictionary.' % fetches_dict)

        import tensorflow as tf
        default_graph = tf.get_default_graph()

        for name, fetch in fetches_dict.items():
            if not isinstance(name, string_types):
                raise ValueError("monitored metrics key %s is not a string" % name)

            try:
                default_graph.as_graph_element(fetch, allow_tensor=True, allow_operation=False)
            except TypeError as e:
                raise TypeError('Fetch %r has invalid type %r, must be a string or Tensor. (%s)'
                                % (fetch, type(fetch), str(e)))
            except ValueError as e:
                raise ValueError('Fetch %r cannot be interpreted as a Tensor. (%s)' % (fetch, str(e)))
            except KeyError as e:
                raise ValueError('Fetch %r cannot be found in the default graph. (%s)' % (fetch, str(e)))

    def _validate_monitored_fetches(self, monitored_fetches, raise_exception=True):
        try:
            self._validate_fetches_dict(monitored_fetches)
        except Exception as ex:
            self.logger.warning(ex)
            if raise_exception:
                raise

    @staticmethod
    def _validate_custom_metrics_dict(custom_metrics):
        if custom_metrics is None:
            return

        if not isinstance(custom_metrics, dict):
            raise ValueError('Custom metrics %s must be a dictionary.' % custom_metrics)

        for name, metric_func in custom_metrics.items():
            if not isinstance(name, string_types):
                raise ValueError("Custom metric's key %s is not a string" % name)

            if not callable(metric_func):
                raise ValueError('Custom metric function of %s must be callable' % name)

    def _validate_custom_metrics(self, custom_metrics, raise_exception=True):
        try:
            self._validate_custom_metrics_dict(custom_metrics)
        except Exception as ex:
            self.logger.warning(ex)
            if raise_exception:
                raise

    @staticmethod
    def _generate_unique_key(existing_keys):
        while True:
            key = BaseCallback.generate_tag()
            if key not in existing_keys:
                return key

    @staticmethod
    def _total_epochs(max_iterations, epoch_size):
        if not max_iterations or not epoch_size:
            return None

        return max_iterations // epoch_size

    # region - ModelHashInterface

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

        variables = tf.trainable_variables()

        if type(session) in _TF_PATCHED_RUN:
            # `tf.Session.run` is being patched. Use the original method to
            # avoid possible infinite recursion caused by the patched method.
            return _TF_PATCHED_RUN[type(session)](session, variables)

        return session.run(variables)

    def get_weights_hash(self, session):
        try:
            return self.calculate_weights_hash(session)
        except Exception:
            self.logger.exception("Was not able to calculate weights hash for new TF API")
            return None

    def _get_structure_hash(self, session):
        import tensorflow as tf

        variables = tf.trainable_variables()
        shapes = tuple([tuple(x.get_shape().as_list()) for x in variables])
        return hash_value(shapes)

    # endregion

    def __get_tensor_from_op(self, op):
        outputs = op.outputs
        if len(outputs) > 1:
            self.logger.warning("Length of outputs of 'op' is %s", len(outputs))
        elif len(outputs) == 0:
            raise MissingLinkException("Operation node has empty 'outputs'")
        return outputs[0]

    def _get_tensor_from_name(self, model, name, by_attr, expect_many=False, return_many=False, reverse_order=True):
        name = str(name).lower()
        operations = model.graph.get_operations()
        if reverse_order:
            operations = operations[::-1]     # will start seeking from the end
        ops = [op for op in operations if str(getattr(op, by_attr)).lower() == name]
        if len(ops) > 1 and not expect_many:
            self.logger.warning("Unexpected length of ops %s retrieved by op.%s=%s", len(ops), by_attr, name)
        elif len(ops) == 0:
            self.logger.warning("No op found by op.%s=%s", by_attr, name)
            return None
        if return_many:
            tensors = [self.__get_tensor_from_op(i) for i in ops]
            return tensors
        single_op = ops[0]
        tensor = self.__get_tensor_from_op(single_op)
        return tensor

    def _determine_input_placeholder(self, model):
        input_placeholder = self._properties.get("__input_placeholder")
        if input_placeholder is not None:
            return input_placeholder
        pl_name = self._properties.get("input_placeholder")
        if pl_name is not None:
            pl = self._get_tensor_from_name(model, pl_name, "name", reverse_order=False)
        else:
            pl = self._get_tensor_from_name(model, "placeholder", "type", reverse_order=False)
        if pl is None:
            message = "Cannot infer placeholder for input data. " \
                      "Please use 'set_properties' and specify 'input_placeholder'. " \
                      "e.g. experiment.set_properties(input_placeholder=X)"
            self.logger.error(message)
            raise MissingLinkException(message)
        self._properties["__input_placeholder"] = pl  # note: here we save a placeholder instance, not a name
        return pl

    def _get_input_dim(self, model):
        pl = self._determine_input_placeholder(model)
        try:
            shape = pl.shape.as_list()
        except ValueError as ex:
            self.logger.exception(ex)
            raise MissingLinkException("Was not able to determine input shape. Please set it via set_properties!")
        shape = shape[1:]       # excluding batch size
        h, w, d = shape
        shape = (d, h, w)       # shape has to be in format: depth, height, width regardless of framework ordering
        return shape

    def _get_prediction(self, model, image, shape=None):
        input_, depth, height, width = self._get_scaled_input(image, shape)
        output_layer_name = self._properties.get("output_layer")
        if output_layer_name is not None:
            output_layer = self._get_tensor_from_name(model, output_layer_name, "name")
        else:
            output_layer = self._get_tensor_from_name(model, "softmax", "type")
        if output_layer is None:
            raise MissingLinkException("Please provide output operation via set_properties. "
                                       "e.g. experiment.set_properties(output_layer='softmax')")
        self._properties["__output_layer"] = output_layer
        input_placeholder = self._determine_input_placeholder(model)
        probs = model.run(output_layer, feed_dict={input_placeholder: np.array([input_])})
        probs = np.squeeze(probs)
        return input_, probs

    def _get_activation_and_grad_for_last_conv(self, model, scores, input_=None):
        import tensorflow as tf

        last_conv_layer_name = self._properties.get("last_conv_layer")
        if last_conv_layer_name:
            last_conv = self._get_tensor_from_name(model, last_conv_layer_name, "name")
        else:
            last_conv = self._get_tensor_from_name(model, "conv2d", "type", expect_many=True)
        if last_conv is None:
            raise MissingLinkException("Cannot determine last convolutional layer. Try to provide name of last conv "
                                       "layer explicitly via set_properties. "
                                       "e.g. experiment.set_properties(last_conv_layer='conv5_3/conv2d')")
        output_layer = self._properties["__output_layer"]
        input_placeholder = self._determine_input_placeholder(model)

        signal = tf.multiply(output_layer, scores)
        loss = tf.reduce_mean(signal)
        grads = tf.gradients(loss, last_conv)[0]
        normalize_grads = tf.div(grads, tf.sqrt(tf.reduce_mean(tf.square(grads))) + tf.constant(1e-5))
        output, grads_val = model.run([last_conv, normalize_grads], feed_dict={input_placeholder: np.array([input_])})

        grads_val = grads_val[0]
        a_weights = np.mean(grads_val, axis=(0, 1))
        return output, a_weights

    def generate_grad_cam(self, uri=None, model=None, input_array=None, top_classes=5, top_images=1, class_mapping=None,
                          dim_order=ImageDimOrdering.NHWC, expected_class=None, keep_origin=False, description=None):
        try:
            images_data, top = self._generate_grad_cam(
                model, uri=uri, input_array=input_array, top_classes=top_classes, top_images=top_images,
                class_mapping=class_mapping, dim_order=dim_order, logger=self.logger)
        except MissingLinkException:
            self.logger.exception("Was not able to produce GradCAM images because of internal error!")
        else:
            images = self.callback._prepare_images_payload(images_data, keep_origin, uri)
            meta = self.callback._get_toplevel_metadata(self.callback._test_token, AlgorithmTypes.GRAD_CAM, uri)
            extra = {
                "expected_class": expected_class,
                "top": top,
            }
            meta.update(extra)
            model_hash = self.get_weights_hash(model)
            self.callback.upload_images(model_hash, images, meta, description=description)

    def _get_feature_maps(self, model, image, shape=None):
        input_, depth, height, width = self._get_scaled_input(image, shape)
        output_layer_name = self._properties.get("output_layer")
        if output_layer_name is None:
            raise MissingLinkException("Please provide 'output_layer' via set_properties.")
        output_layer = self._get_tensor_from_name(model, output_layer_name, "name")
        if output_layer is None:
            raise MissingLinkException("Was not able to find op named %s" % output_layer_name)

        all_conv = self._get_tensor_from_name(model, "conv2d", "type", expect_many=True, return_many=True,
                                              reverse_order=False)
        if len(all_conv) == 0:
            raise MissingLinkException("Was not able to determine Conv2D layers in the network. "
                                       "Make sure you have some.")
        input_placeholder = self._determine_input_placeholder(model)
        all_conv.append(output_layer)
        result = model.run(all_conv, feed_dict={input_placeholder: np.array([input_])})
        maps = result[:-1]
        output = result[-1]
        return maps, output

    def visual_back_prop(self, uri=None, model=None, input_val=None, dim_order=ImageDimOrdering.NHWC,
                         expected_output=None, keep_origin=False, description=None):
        try:
            result = self._visual_back_prop(model, uri=uri, input_val=input_val, dim_order=dim_order,
                                            logger=self.logger)
        except MissingLinkException:
            self.logger.exception("Was not able to generate image with VisualBackProp because of internal error!")
        else:
            images = self.callback._prepare_images_payload(result, keep_origin, uri)
            meta = self.callback._get_toplevel_metadata(self.callback._test_token, AlgorithmTypes.VISUAL_BACKPROP, uri)
            extra = {
                "expected_output": expected_output
            }
            meta.update(extra)
            model_hash = self.get_weights_hash(model)
            self.callback.upload_images(model_hash, images, meta, description=description)


class Context(object):
    EXPERIMENT = 'experiment'
    LOOP = 'loop'
    EPOCH_LOOP = 'epoch_loop'
    BATCH_LOOP = 'batch_loop'
    TRAIN = 'train'
    TEST = 'test'
    VALIDATION = 'validation'


class ContextValidator(object):
    """This class validates if we can enter or exit a context.
    """
    def __init__(self, logger):
        self._contexts = []
        self._logger = logger

    def enter(self, context):
        map_context_to_validator = {
            Context.EXPERIMENT: self._validate_experiment_context,
            Context.LOOP: self._validate_loop_context,
            Context.EPOCH_LOOP: self._validate_epoch_loop_context,
            Context.BATCH_LOOP: self._validate_batch_loop_context,
            Context.TRAIN: self._validate_train_context,
            Context.VALIDATION: self._validate_validation_context,
            Context.TEST: self._validate_test_context
        }
        try:
            map_context_to_validator[context]()
        except KeyError:
            # This should never happen unless we mess up
            raise MissingLinkException('Unknown scope %s' % context)

        self._contexts.append(context)

    def exit(self, context):
        last_context = self._contexts.pop()

        if last_context != context:
            # This should never happen unless we mess up
            raise MissingLinkException('Cannot exit %s scope because the current scope is %s' % (context, last_context))

    @property
    def _last_context(self):
        return self._contexts[len(self._contexts) - 1]

    def _validate_test_context(self):
        cant_enter_test_context = \
            not self._contexts or self._last_context not in [Context.EXPERIMENT, Context.LOOP, Context.EPOCH_LOOP,
                                                             Context.BATCH_LOOP]
        if cant_enter_test_context:
            self._logger.warning('cannot enter `test` context. Last context is %s', self._last_context)

    def _validate_experiment_context(self):
        if self._contexts:
            raise MissingLinkException('Experiment context must be outermost')

    def _validate_loop_context(self):
        if not self._contexts or self._last_context != Context.EXPERIMENT:
            raise MissingLinkException('`loop` must be nested immediately in an `experiment` context.')

    def _validate_epoch_loop_context(self):
        if not self._contexts or self._last_context != Context.EXPERIMENT:
            raise MissingLinkException('`epoch_loop` must be nested immediately in an `experiment` context.')

    def _validate_batch_loop_context(self):
        if not self._contexts or self._last_context != Context.EPOCH_LOOP:
            raise MissingLinkException('`batch_loop` must be nested immediately in an `epoch_loop` generator.')

    def _validate_train_context(self):
        if not self._contexts or self._last_context not in [Context.LOOP, Context.BATCH_LOOP]:
            raise MissingLinkException('`train` context must be nested immediately in an `loop` '
                                       'or `batch_loop` generator.')

    def _validate_validation_context(self):
        if not self._contexts or self._last_context not in [Context.LOOP, Context.EPOCH_LOOP, Context.BATCH_LOOP]:
            # Do not raise exception because we don't want to halt the experiment halfway
            self._logger.error('`validation` context must be nested immediately in a `loop` '
                               'or `epoch_loop` or `batch_loop` generator. This context is ignored')

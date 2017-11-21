# coding=utf-8
from __future__ import absolute_import

import copy
import math
from contextlib import contextmanager

import numpy as np
import warnings

from missinglink_kernel.callback.utilities.utils import hasharray, hashcombine
from .base_callback import BaseCallback, WEIGHTS_HASH_PREFIX
from .exceptions import MissingLinkException
from .interfaces import ModelHashInterface, GradCAMInterface, ImageDimOrdering, VisualBackPropInterface
from .settings import HyperParamTypes, MetricPhasePrefixes, AlgorithmTypes


class KerasCallback(BaseCallback, ModelHashInterface, GradCAMInterface, VisualBackPropInterface):
    def __init__(self, owner_id, project_token, stopped_callback=None, host=None):
        super(KerasCallback, self).__init__(
            owner_id, project_token, stopped_callback=stopped_callback, host=host, framework='keras')
        self.token = project_token
        self.current_epoch = 0
        self.params = {}
        self.model = None

    # Deprecated. To support Keras v1
    def _set_params(self, params):
        self.params = self._params_v2_from_v1(params)

    # Deprecated. To support Keras v1
    def _set_model(self, model):
        self.model = model

    def set_params(self, params):
        self.params = params

    def set_model(self, model):
        self.model = model

    @classmethod
    def _prefix_metric(cls, metric):
        keras_validation_prefix_string = 'val_'
        if metric.startswith(keras_validation_prefix_string):
            return MetricPhasePrefixes.VAL + metric[len(keras_validation_prefix_string):]
        return MetricPhasePrefixes.TRAIN + metric

    def on_train_begin(self, logs=None):
        params = copy.copy(self.params)
        self.set_hyperparams(
            total_epochs=params.get('epochs'),
            batch_size=params.get('batch_size'),
            samples_count=params.get('samples') or params.get("sample"))
        if 'metrics' in params:
            params['metrics'] = [self._prefix_metric(name) for name in params.get('metrics')]
        self._extract_hyperparams_from_optimizer(self.model.optimizer)
        structure_hash = self._get_structure_hash(self.model)
        self.train_begin(params, structure_hash=structure_hash)

    def on_train_end(self, logs=None):
        self._train_end(metricData=self._latest_metrics)

    def on_epoch_begin(self, epoch, logs=None):
        self.current_epoch = epoch

        self.epoch_begin(epoch)

    def on_epoch_end(self, epoch, logs=None):
        model_hash = self.get_weights_hash(self.model)
        ml_prefixed_metrics_dict = {self._prefix_metric(name): value for name, value in logs.items()}
        self.epoch_end(epoch, ml_prefixed_metrics_dict, weights_hash=model_hash)

    def on_batch_begin(self, batch, logs=None):
        self.batch_begin(batch, self.current_epoch)

    def _is_last_batch(self, batch):
        if 'samples' not in self.params or 'batch_size' not in self.params:
            return False

        batches = self.params['samples'] / self.params['batch_size']
        return batch == batches - 1

    def _is_last_epoch(self, epoch):
        return epoch == self.params['epochs'] - 1

    def on_batch_end(self, batch, logs=None):
        metric_data = {metric: logs[metric] for metric in self.params['metrics'] if metric in logs}
        ml_prefixed_metrics_dict = {self._prefix_metric(name): value for name, value in metric_data.items()}
        self.batch_end(batch, self.current_epoch, ml_prefixed_metrics_dict)

    @classmethod
    def calculate_weights_hash(cls, net):
        weight_hashes = []
        for layer in net.layers:
            weights = layer.get_weights()
            if weights is None:
                continue

            for weight in weights:
                weight_hashes.append(hasharray(weight))

        return WEIGHTS_HASH_PREFIX + hashcombine(*weight_hashes)

    @classmethod
    def variable_to_value(cls, variable):
        class_name = variable.__class__.__name__
        if class_name == 'TensorSharedVariable':
            return variable.eval()
        elif class_name == 'Variable' and hasattr(variable, 'initial_value'):
            message = variable.initial_value.op.node_def
            from google.protobuf import json_format

            val = json_format.MessageToDict(message).get('attr', {}) \
                .get('value', {}).get('tensor', {}).get('floatVal')

            if val is None:
                return None

            return np.mean(val)

        return super(KerasCallback, cls).variable_to_value(variable)

    def _get_feature_maps(self, model, image, shape=None):
        from .vis.dynamic_import import DynamicImport

        dynamic_import = DynamicImport(model)
        keras_backend = dynamic_import.bring('backend')
        Convolution2D = dynamic_import.bring('layers.Convolution2D')
        dim_ordering = keras_backend.image_dim_ordering()
        channels_first = dim_ordering == 'th'

        input_, depth, height, width = self._get_scaled_input(image, shape)
        if channels_first:
            input_ = input_.transpose(2, 0, 1)

        layer_indexes = [ind for ind, el in enumerate(model.layers) if isinstance(el, Convolution2D)]
        layers = [model.layers[li].output for li in layer_indexes]
        get_feature = keras_backend.function([model.layers[0].input], layers)
        output = model.predict(np.expand_dims(input_, axis=0))
        feature_maps = get_feature([[input_]])
        return feature_maps, output

    @classmethod
    def _get_input_dim(cls, model):
        from .vis.dynamic_import import DynamicImport

        dynamic_import = DynamicImport(model)
        keras_backend = dynamic_import.bring('backend')
        dim_ordering = keras_backend.image_dim_ordering()
        channels_first = dim_ordering == 'th'

        if channels_first:
            # it means we have NCHW ordering
            _, depth, height, width = model.input_shape
        else:
            # we have NHWC ordering
            _, height, width, depth = model.input_shape
        return depth, height, width

    @classmethod
    def _get_activation_and_grad_for_last_conv(cls, model, scores, input_=None):
        from .vis.dynamic_import import DynamicImport

        dynamic_import = DynamicImport(model)
        Convolution2D = dynamic_import.bring('layers.Convolution2D')
        Lambda = dynamic_import.bring('layers.core.Lambda')
        Sequential = dynamic_import.bring('models.Sequential')
        K = dynamic_import.bring('backend')

        def normalize(x):
            # utility function to normalize a tensor by its L2 norm
            return x / (K.sqrt(K.mean(K.square(x))) + 1e-5)

        def target_category_loss(x, category_index, nb_classes):
            return K.batch_dot(x, K.one_hot([category_index], nb_classes), axes=(1, 1))

        def target_category_loss_output_shape(input_shape):
            return input_shape

        def target_layer(x):
            return target_category_loss(x, pred_class, scores.shape[0])

        pred_class = np.argmax(scores)
        result_model = Sequential()
        result_model.add(model)
        result_model.add(Lambda(target_layer, output_shape=target_category_loss_output_shape))
        conv_layer_indexes = [i for i, layer in enumerate(model.layers) if isinstance(layer, Convolution2D)]
        if not conv_layer_indexes:
            raise MissingLinkException("Unable to find convolutional layer in the model!")

        conv_output = model.layers[conv_layer_indexes[-1]].output
        loss = K.sum(result_model.layers[-1].output)
        grads = normalize(K.gradients(loss, conv_output)[0])
        gradient_function = K.function([result_model.layers[0].input], [conv_output, grads])
        output, grads_val = gradient_function([np.expand_dims(input_, axis=0)])

        dim_ordering = K.image_dim_ordering()
        channels_first = dim_ordering == 'th'
        axis = (1, 2) if channels_first else (0, 1)
        a_weights = np.mean(grads_val[0], axis=axis)

        return output, a_weights

    def _get_prediction(self, model, image, shape=None):
        from .vis.dynamic_import import DynamicImport

        dynamic_import = DynamicImport(model)
        keras_backend = dynamic_import.bring('backend')
        dim_ordering = keras_backend.image_dim_ordering()
        channels_first = dim_ordering == 'th'

        input_, depth, height, width = self._get_scaled_input(image, shape)
        if channels_first:
            input_ = input_.transpose(2, 0, 1)
        probs = model.predict(np.array([input_]))
        probs = np.squeeze(probs)
        return input_, probs

    def process_image(self, path=None, model=None, upload_images=None, seed_image=None):
        from .vis.dynamic_import import DynamicImport

        warnings.warn("This method is deprecated. use 'generate_grad_cam' instead", DeprecationWarning)
        dynamic_import = DynamicImport(model)
        keras_backend = dynamic_import.bring('backend')
        dim_ordering = keras_backend.image_dim_ordering()
        channels_first = dim_ordering == 'th'

        dim_order = ImageDimOrdering.NCHW if channels_first else ImageDimOrdering.NHWC

        self.generate_grad_cam(path, model, input_array=seed_image, dim_order=dim_order)

    def generate_grad_cam(self, uri=None, model=None, input_array=None, top_classes=5, top_images=1, class_mapping=None,
                          dim_order=ImageDimOrdering.NHWC, expected_class=None, keep_origin=False, description=None):
        try:
            images_data, top = self._generate_grad_cam(
                model, uri=uri, input_array=input_array, top_classes=top_classes, top_images=top_images,
                class_mapping=class_mapping, dim_order=dim_order, logger=self.logger)
        except MissingLinkException:
            self.logger.exception("Was not able to produce GradCAM images because of internal error!")
        else:
            images = self._prepare_images_payload(images_data, keep_origin, uri)
            meta = self._get_toplevel_metadata(self._test_token, AlgorithmTypes.GRAD_CAM, uri)
            extra = {
                "expected_class": expected_class,
                "top": top,
            }
            meta.update(extra)
            model_hash = self.get_weights_hash(model)
            self.upload_images(model_hash, images, meta, description=description)

    def visual_back_prop(self, uri=None, model=None, input_val=None, dim_order=ImageDimOrdering.NHWC,
                         expected_output=None, keep_origin=False, description=None):
        try:
            result = self._visual_back_prop(model, uri=uri, input_val=input_val, dim_order=dim_order,
                                            logger=self.logger)
        except MissingLinkException:
            self.logger.exception("Was not able to generate image with VisualBackProp because of internal error!")
        else:
            images = self._prepare_images_payload(result, keep_origin, uri)
            meta = self._get_toplevel_metadata(self._test_token, AlgorithmTypes.VISUAL_BACKPROP, uri)
            extra = {
                "expected_output": expected_output
            }
            meta.update(extra)
            model_hash = self.get_weights_hash(model)
            self.upload_images(model_hash, images, meta, description=description)

    # region ModelHashInterface

    def get_weights_hash(self, net):
        return self.calculate_weights_hash(net)

    def _get_structure_hash(self, net):
        layers_repr = []
        # noinspection PyBroadException
        try:
            for i, layer in enumerate(net.layers):
                inbound_nodes = layer.inbound_nodes
                if not inbound_nodes:
                    continue

                inbound_node_shapes = [tuple(layer.get_input_shape_at(index)) for index in range(len(inbound_nodes))]
                inbound_node_shapes = tuple(inbound_node_shapes) if len(inbound_node_shapes) > 1 \
                    else inbound_node_shapes[0]
                layer_bias = getattr(layer, 'use_bias', None)
                layer_type = type(layer)
                layers_repr.append((layer_type, inbound_node_shapes, layer_bias))
            return self._hash(tuple(layers_repr))
        except Exception:
            self.logger.exception('Failed to calculate the structural hash')
            return None

    # endregion
    @classmethod
    def _params_v2_from_v1(cls, params_v1):
        params_v2 = params_v1.copy()
        params_v2['epochs'] = params_v1['nb_epoch']
        params_v2['samples'] = params_v1['nb_sample']
        return params_v2

    def _extract_hyperparams_from_optimizer(self, optimizer):
        optimizer_hyperparams = {
            'SGD': ['lr', 'momentum', 'decay', 'nesterov'],
            'RMSprop': ['lr', 'rho', 'epsilon', 'decay'],
            'Adagrad': ['lr', 'epsilon', 'decay'],
            'Adadelta': ['lr', 'rho', 'epsilon', 'decay'],
            'Adam': ['lr', 'beta_1', 'beta_2', 'epsilon', 'decay'],
            'Adamax': ['lr', 'beta_1', 'beta_2', 'epsilon', 'decay'],
            'Nadam': ['lr', 'beta_1', 'beta_2', 'epsilon', 'schedule_decay'],
        }
        hyperparam_names = {
            'lr': 'learning_rate',
            'decay': 'learning_rate_decay',
        }

        self.set_hyperparams(optimizer_algorithm=optimizer.__class__.__name__)
        self._extract_hyperparams(HyperParamTypes.OPTIMIZER, optimizer, optimizer_hyperparams, hyperparam_names)

    @contextmanager
    def test(self, model=None):
        if not self.has_experiment:
            self.new_experiment()

        model = model or self.model
        self.set_model(model)

        self._patch_evaluate_generator()
        self._patch_test_loop()
        self._patch_test_function()

        yield self

        self._unpatch_evaluate_generator()
        self._unpatch_test_loop()
        self._unpatch_test_function()

    def _create_test_function(self, original_test_function):
        def predict_classes(x, batch_size):
            proba = self.model.predict(x, batch_size=batch_size)

            return proba.argmax(axis=-1), proba.max(axis=-1)

        def test_function(ins_batch):
            number_of_inputs = len(self.model.inputs)
            predictions, probabilities = predict_classes(ins_batch[:number_of_inputs], batch_size=len(ins_batch[0]))
            expected = np.argmax(ins_batch[number_of_inputs], axis=1)
            result = original_test_function(ins_batch)

            expected = expected.tolist()
            predictions = predictions.tolist()
            probabilities = probabilities.tolist()

            self._test_iteration_end(expected, predictions, probabilities)
            return result

        return test_function

    def _on_test_begin(self, steps):
        weights_hash = self.get_weights_hash(self.model)

        if weights_hash is None:
            # TODO warn
            return

        self._test_begin(steps, weights_hash)

    def _ml_evaluate_generator(
            self,
            generator,
            steps,
            max_queue_size=10,
            workers=1,
            use_multiprocessing=False):

        self._on_test_begin(steps)

        return self._evaluate_generator(
            generator, steps, max_queue_size=max_queue_size, workers=workers, use_multiprocessing=use_multiprocessing)

    def _ml_test_loop(self, f, ins, batch_size=32, verbose=0, steps=None):
        temp_steps = steps
        if temp_steps is None:
            if ins and hasattr(ins[0], 'shape'):
                test_samples_count = ins[0].shape[0]
            else:
                test_samples_count = batch_size
            temp_steps = int(np.ceil(test_samples_count / float(batch_size)))

        self._on_test_begin(temp_steps)

        if steps is None:
            return self._test_loop(f, ins, batch_size, verbose)
        else:
            return self._test_loop(f, ins, batch_size, verbose, temp_steps)

    def _get_training_model(self):
        if hasattr(self.model, 'model') and hasattr(self.model.model, 'test_function'):
            return self.model.model

        return self.model

    def _patch_evaluate_generator(self):
        training_model = self._get_training_model()

        self._evaluate_generator = training_model.evaluate_generator
        training_model.evaluate_generator = self._ml_evaluate_generator

    def _patch_test_loop(self):
        training_model = self._get_training_model()

        # noinspection PyProtectedMember
        self._test_loop = training_model._test_loop
        training_model._test_loop = self._ml_test_loop

    def _patch_test_function(self):
        training_model = self._get_training_model()

        # noinspection PyProtectedMember
        training_model._make_test_function()

        temp_test = training_model.test_function

        training_model.test_function = self._create_test_function(temp_test)

    def _unpatch_evaluate_generator(self):
        training_model = self._get_training_model()

        training_model.evaluate_generator = self._evaluate_generator
        del self._evaluate_generator

        training_model.test_function = None

    def _unpatch_test_loop(self):
        training_model = self._get_training_model()

        training_model._test_loop = self._test_loop

        del self._test_loop

    def _unpatch_test_function(self):
        training_model = self._get_training_model()

        training_model.test_function = None

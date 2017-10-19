# coding=utf-8
import numpy as np
import os
import six
import warnings
from os import path

from missinglink_kernel.callback.utilities.utils import enum
from missinglink_kernel.callback.utilities.utils import hasharray, hashcombine
from .base_callback import BaseCallback, WEIGHTS_HASH_PREFIX
from .exceptions import MissingLinkException
from .interfaces import ModelHashInterface, GradCAMInterface, VisualBackPropInterface, ImageDimOrdering
from .settings import HyperParamTypes, MetricPhasePrefixes, MetricTypePrefixes, AlgorithmTypes
from .state_counter import StateCounter

prototext_type = enum('solver', 'net')


# noinspection PyUnresolvedReferences
def create_caffe_solver():
    from caffe.proto import caffe_pb2

    return caffe_pb2.SolverParameter()


# noinspection PyUnresolvedReferences
def create_caffe_net():
    from caffe.proto import caffe_pb2

    return caffe_pb2.NetParameter()


def parse_prototxt(prototext_path, file_type):
    if not path.exists(prototext_path):
        raise MissingLinkException('file not found %s' % prototext_path)

    from google.protobuf import json_format, text_format

    with open(prototext_path) as f:
        raw_solver = f.read()

    if file_type == prototext_type.solver:
        message = create_caffe_solver()
    elif file_type == prototext_type.net:
        message = create_caffe_net()
    else:
        raise MissingLinkException('unknown file_type %s' % file_type)

    text_format.Merge(raw_solver, message)
    solver = json_format.MessageToDict(message)
    return solver


class PyCaffeCallback(BaseCallback, ModelHashInterface, GradCAMInterface, VisualBackPropInterface):
    def __init__(self, owner_id, project_token, stopped_callback=None, host=None):
        super(PyCaffeCallback, self).__init__(owner_id, project_token, stopped_callback=stopped_callback,
                                              host=host, framework='pycaffe')
        self.state_counter = StateCounter(self)
        self.has_started = False
        self.monitored_blobs = []
        self.custom_monitored_blobs = []
        self.batches_per_epoch = None
        self._snapshot_interval = None
        self._max_iterations = None
        self.solver = None
        self.test_iter = None
        self.test_interval = None
        self._expected_layer_name = 'label'
        self._predictions_layer_name = 'score'

    @property
    def _is_snapshot_iteration(self):
        if self._snapshot_interval is None:
            return False

        return self.iteration % self._snapshot_interval == 0

    @property
    def _is_epoch_iteration(self):
        if self.batches_per_epoch is None:
            return False

        return self.iteration % self.batches_per_epoch == 0

    @property
    def _is_last_step(self):
        if self._max_iterations is None:
            return False

        return self.iteration >= self._max_iterations

    @property
    def _is_test_iteration(self):
        if not self.test_interval:
            return False

        return self.iteration % self.test_interval == 0

    @classmethod
    def calculate_weights_hash(cls, net):
        layer_names = list(net._layer_names)
        layer_hashes = []
        for layer in layer_names:
            weights = net.params.get(layer)
            if not weights:
                continue

            weights = weights[0].data
            layer_hash = hasharray(weights)
            layer_hashes.append(layer_hash)

        return WEIGHTS_HASH_PREFIX + hashcombine(*layer_hashes)

    def set_monitored_blobs(self, blobs='loss'):
        if isinstance(blobs, six.string_types):
            blobs = [blobs]

        for blob in blobs:
            lst = self.custom_monitored_blobs if callable(blob) else self.monitored_blobs
            lst.append(blob)

    def prepare_for_begin(self, solver_class, solver_params):
        self.hyperparams_from_solver(solver_class, solver_params)
        run_hyperparameter = self.get_hyperparams().get('run', {})

        epoch_size = run_hyperparameter.get('epoch_size')
        self._snapshot_interval = solver_params.get('snapshot')

        if epoch_size is None:
            self.logger.debug('Epoch size is None')
            self.set_hyperparams(total_batches=self._max_iterations)
        else:
            batch_size = run_hyperparameter.get('batch_size')

            if batch_size is None:
                raise MissingLinkException('Batch_size cannot be None')

            self.batches_per_epoch = epoch_size

            total_epochs = int(self._max_iterations / self.batches_per_epoch) if self._max_iterations is not None else None

            self.set_hyperparams(total_epochs=total_epochs, total_batches=self._max_iterations)

    def set_expected_predictions_layers(self, expected_layer_name, predictions_layer_name):
        self._expected_layer_name = expected_layer_name
        self._predictions_layer_name = predictions_layer_name

    def create_wrapped_solver(self, solver_class, prototext_path=None, solver_params=None):
        if solver_params is None:
            if os.path.exists(prototext_path):
                solver_params = parse_prototxt(prototext_path, prototext_type.solver)
            else:
                solver_params = {}

        self.test_iter = solver_params.get('testIter')
        if self.test_iter is not None:
            del solver_params['testIter']

        self.test_interval = solver_params.get('testInterval')
        if self.test_interval is not None:
            del solver_params['testInterval']

        self._max_iterations = solver_params.get('maxIter', 0)

        callback = self

        class WrappedSolver(solver_class):
            def __init__(self, path):
                super(WrappedSolver, self).__init__(path)

            def step(self, batches):
                if batches > 0 and not callback.has_started:
                    callback.prepare_for_begin(solver_class, solver_params)
                    callback.train_begin(solver_params, structure_hash=callback._get_structure_hash(self.net))
                    callback.has_started = True

                ret = None

                for i in range(batches):
                    callback.before_step(1)
                    ret = solver_class.step(self, 1)
                    metric_data = self.get_blobs(self.net)

                    if not metric_data:
                        self.logger.warning('no blobs are being monitored')

                    callback.after_step(metric_data)

                return ret

            def solve(self):
                if not callback._max_iterations:
                    callback.logger.warning('maxIter is 0. The experiment will not be monitored')

                self.step(callback._max_iterations)

            def _forward_test_net(self, blobs=None, start=None, end=None, index=0, **kwargs):
                net = self.test_nets[index]
                return net.forward(blobs, start, end, **kwargs)

            def has_layes(self, net, layer_names):
                for layer_name in layer_names:
                    if layer_name not in net.blobs:
                        return False

                return True

            def forward_test_net_all(self, weights_hash, blobs=None, start=None, end=None, index=0, **kwargs):
                net = self.test_nets[index]

                ret = {}
                callback._test_begin(callback.test_iter[index], weights_hash)

                test_layers = [callback._expected_layer_name, callback._predictions_layer_name]
                found_layer_names = self.has_layes(net, test_layers)
                if not found_layer_names:
                    callback.logger.warning(
                        'could not find layer "%s" and "%s" in test net #%s to generate confusion matrix',
                        callback._expected_layer_name, callback._predictions_layer_name, index)

                for i in range(callback.test_iter[index]):
                    net.forward(blobs, start, end, **kwargs)

                    if found_layer_names:
                        expected = map(int, net.blobs[callback._expected_layer_name].data) if callback._expected_layer_name in net.blobs else []
                        predictions = np.argmax(net.blobs[callback._predictions_layer_name].data, axis=1) if callback._predictions_layer_name in net.blobs else []
                        probabilities = np.max(net.blobs[callback._predictions_layer_name].data, axis=1) if callback._predictions_layer_name in net.blobs else []
                    else:
                        expected = []
                        predictions = []
                        probabilities = []

                    callback._test_iteration_end(expected, predictions, probabilities)

                return self.get_blobs(net)

            @classmethod
            def forward_test_net(cls, blobs=None, start=None, end=None, index=0, **kwargs):
                warnings.warn("This method is deprecated", DeprecationWarning)

            @staticmethod
            def get_blobs(net):
                metric_data = {}
                if len(net.outputs) == 0:
                    self.warn_no_outputs()
                elif len(self.monitored_blobs) == 0:
                    self.set_monitored_blobs(net.outputs)
                elif len(self.monitored_blobs) > 0 and self._is_first_iteration:
                    not_monitored = [out_blob for out_blob in net.outputs if out_blob not in self.monitored_blobs]
                    not_exists = [out_blob for out_blob in self.monitored_blobs if out_blob not in net.outputs]

                    if len(not_monitored) > 0:
                        self.warn_not_monitored(not_monitored)

                    if len(not_exists) > 0:
                        self.warn_not_exists(not_exists)

                for blob_name in self.monitored_blobs:
                    blob = net.blobs.get(blob_name)
                    if blob is None:
                        self.logger.warning('%s blob does not exist in net and will not be monitored', blob_name)
                        continue

                    value = np.copy(blob.data)

                    if np.shape(value) == ():
                        metric_data[blob_name] = value
                        continue

                    blob_name += '_mean'
                    metric_data[blob_name] = np.mean(value)

                for blob_function in self.custom_monitored_blobs:
                    metric_data[MetricTypePrefixes.CUSTOM + blob_function.__name__] = blob_function()

                return metric_data

        self.solver = WrappedSolver(prototext_path)

        batch_size = self._get_batch_size(self.solver.net)
        self.set_properties(batch_size=batch_size)

        return self.solver

    def _get_batch_size(self, net):
        try:
            input_layer = net.layer_dict.keys()[0]
            input_shape = net.blobs[input_layer].shape
            return input_shape[0]
        except Exception as ex:
            self.logger.warning('Failed to extract the batch_size %s', ex)
            return None

    def warn_no_outputs(self):
        self.logger.warning(
            'your net doesn\'t have any outputs please check your configuration')

    def warn_not_monitored(self, not_monitored):
        self.logger.warning(
            'your net have outputs that you are not monitoring: %s', ', '.join(not_monitored))

    def warn_not_exists(self, not_exists):
        self.logger.warning(
            'your config have monitored metrics that not exists in the network: %s', ', '.join(not_exists))

    def end_train(self):
        warnings.warn("This method is deprecated", DeprecationWarning)
        self._train_end()

    def before_step(self, batches):
        epoch = self.state_counter.epoch
        if self.batches_per_epoch is not None:
            if self.state_counter.batch >= self.batches_per_epoch:
                epoch += 1

        self.state_counter.batch += batches - 1
        self.state_counter.begin_batch(epoch)

    def after_step(self, metric_data):
        weights_hash = None
        is_test = None

        if self._is_snapshot_iteration and weights_hash is None:
            weights_hash = weights_hash or self.get_weights_hash(self.solver.net)

        metric_data = self._prefix_metric_data(metric_data, MetricPhasePrefixes.TRAIN)

        if self._is_test_iteration:
            weights_hash = weights_hash or self.get_weights_hash(self.solver.net)
            validation_metric_data = self.solver.forward_test_net_all(weights_hash)
            test_metric_data = self._prefix_metric_data(validation_metric_data, MetricPhasePrefixes.VAL)
            metric_data.update(test_metric_data)
            is_test = True

        kwargs = {}

        if weights_hash is not None:
            kwargs['weights_hash'] = weights_hash

        if is_test is not None:
            kwargs['is_test'] = is_test

        is_last_step = self._is_last_step
        is_epoch_iteration = self._is_epoch_iteration

        self.batch_end(
            self.state_counter.batch,
            self.state_counter.epoch, metric_data, **kwargs)

        if is_epoch_iteration:
            weights_hash = weights_hash or self.get_weights_hash(self.solver.net)

            self.epoch_end(self.state_counter.epoch, metric_data, weights_hash=weights_hash)

        if is_last_step:
            self._train_end(metricData=metric_data)

    @classmethod
    def _prefix_metric_data(cls, blobs, prefix):
        metric_data = {}
        for key, value in blobs.items():
            metric_data[prefix + key] = value

        return metric_data

    def hyperparams_from_solver(self, solver_class, solver_params):
        solver_to_attrs = {
            'any': ['baseLr', 'lrPolicy', 'gamma', 'momentum', 'weightDecay']
        }
        attr_to_hyperparam = {
            'baseLr': 'learning_rate',
            'lrPolicy': 'learning_rate_policy',
            'weightDecay': 'weight_decay',
        }

        solver_type = solver_class.__name__
        if solver_type.endswith('Solver'):
            solver_type = solver_type[:-6]

        self.set_hyperparams(optimizer_algorithm=solver_type)
        self._extract_hyperparams(HyperParamTypes.OPTIMIZER, solver_params, solver_to_attrs,
                                  attr_to_hyperparam, object_type='any')

    def test_begin(self, test_iter, model):
        weights_hash = self.get_weights_hash(model)
        self._test_begin(test_iter, weights_hash)

    def test_net_step(self, expected, predictions, probabilities):
        self._test_iteration_end(expected, predictions, probabilities)

    @classmethod
    def __old_caffe_backward_workaround(cls, prob):
        if prob.ndim == 1:
            return prob.reshape(1, 1, 1, prob.shape[0])

        if prob.ndim == 2:
            return prob.reshape(1, 1, prob.shape[0], prob.shape[1])

        if prob.ndim == 3:
            return prob.reshape(1, prob.shape[0], prob.shape[1], prob.shape[1])

        raise MissingLinkException('unsupported shape %s' % prob.ndim)

    @classmethod
    def _get_input_dim(cls, model):
        _, depth, height, width = list(model.blobs["data"].data.shape)
        return depth, height, width

    def _get_feature_maps(self, model, image, shape=None):
        # noinspection PyUnresolvedReferences
        import caffe

        input_, depth, height, width = self._get_scaled_input(image, shape)
        transformer = caffe.io.Transformer({'data': model.blobs['data'].data.shape})
        if depth > 1:  # if image is not grayscale
            transformer.set_transpose('data', (2, 0, 1))
        model.blobs['data'].reshape(*np.asarray([1, depth, height, width]))  # run only one image
        model.blobs['data'].data[...][0, :, :, :] = transformer.preprocess('data', input_)
        out = model.forward()

        layer_names = list(model._layer_names)

        conv_layers_names = [layer_names[index] for index, i in enumerate(model.layers) if i.type == "Convolution"]
        if not conv_layers_names:
            message = "It looks like you model does not have any convolutional layer."
            self.logger.error(message)
            raise MissingLinkException(message)

        activations = [model.blobs[conv].data for conv in conv_layers_names]
        return activations, out

    def _get_prediction(self, net, image, shape=None):
        # noinspection PyUnresolvedReferences
        import caffe

        input_, depth, height, width = self._get_scaled_input(image, shape)
        transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
        if depth > 1:  # if image is not grayscale
            transformer.set_transpose('data', (2, 0, 1))
        net.blobs['data'].reshape(*np.asarray([1, depth, height, width]))  # run only one image
        net.blobs['data'].data[...][0, :, :, :] = transformer.preprocess('data', input_)
        out = net.forward()
        scores = out['prob']
        scores = np.squeeze(scores)
        return input_, scores

    def process_image(self, path, net, scores=None, top_classes=5, top_images=1, class_mapping=None):
        warnings.warn("This method is deprecated. use 'generate_grad_cam' instead", DeprecationWarning)
        self.generate_grad_cam(
            path, net, input_array=None, top_classes=top_classes, top_images=top_images, class_mapping=class_mapping)

    def generate_grad_cam(self, uri=None, model=None, input_array=None, top_classes=5, top_images=1, class_mapping=None,
                          dim_order=ImageDimOrdering.NCHW, expected_class=None, keep_origin=False):
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
            self.upload_images(model_hash, images, meta)

    def visual_back_prop(self, uri=None, model=None, input_val=None, dim_order=ImageDimOrdering.NCHW,
                         expected_output=None, keep_origin=False):
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
            self.upload_images(model_hash, images, meta)

    @classmethod
    def _get_activation_and_grad_for_last_conv(cls, model, scores, input_=None):
        layer_names = list(model._layer_names)
        conv_layers = [index for index, i in enumerate(model.layers) if i.type == "Convolution"]
        if not conv_layers:
            raise MissingLinkException("It looks like you model does not have any convolutional layer. "
                                       "Cannot generate GradCAM.")
        last_conv = layer_names[conv_layers[-1]]    # take the last conv layer
        if len(scores.shape) == 1:  # means it is a 1d array and network expects 2d, so we just add 0 axis
            scores = np.expand_dims(scores, axis=0)
        try:
            diff = model.backward(end=last_conv, prob=scores)
        except Exception as ex:
            # noinspection PyUnresolvedReferences
            if 'diff is not 4-d' in ex.message:
                scores = cls.__old_caffe_backward_workaround(scores)
                diff = model.backward(end=last_conv, prob=scores)
            else:
                # noinspection PyUnresolvedReferences
                raise MissingLinkException(ex.message)
        activation_lastconv = model.blobs[last_conv].data
        grads = model.blobs[last_conv].diff[0]
        # axis here depend on ordering. here it is CHW which is why axis=(1,2) for H and W
        a_weights = np.mean(grads, axis=(1, 2))
        return activation_lastconv, a_weights

    # region ModelHashInterface

    def get_weights_hash(self, net):
        try:
            return self.calculate_weights_hash(net)
        except Exception as ex:
            self.logger.warning('Failed to calculate weights hash %s', ex)
            return None

    def _get_structure_hash(self, net):
        try:
            layers = tuple([i.type for i in net.layers])
            hash_value = self._hash(layers)

            return hash_value
        except Exception as ex:
            self.logger.warning('Failed to calculate structure hash %s', ex)
            return None

    # endregion

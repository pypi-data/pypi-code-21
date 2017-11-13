import tensorflow as tf
from ..graph import Graph, NodeKeys


class Model(Graph):
    """
    Graphs which do not support sofiscated tasks, just acts as an function.

    A Model object is mainly used for two purpose:
        1. Share weights / reuse model for different inputs
        2. Access global configs as it inherent Graph
        3. Use its 'lazy_create' config to for some case of defining graph,
        which is useful for simiplified managing tensorflow name scopes.

    Configs:
        reuse: bool
        tensorflow_variable_scope: str=None, *NOT IMPLEMENTED YET*.
        lazy_create: bool=False, if is True, will not create graph on __init__.

    Model extends Graphs interface with two properities:
        inputs
        outputs
    They are implemented based on nodes.
    Model will generate output tenors in the following two setuations:
        1. when model is created;
        2. when apply (or __call__) method is called.
    You may merge input/output tensors by using 'lazy_create' option, in that case,
    model will not create placeholder inputs, and will generate output tensors in
    the first time it was called.
    """

    def __init__(self, name, inputs=None, child_models=None, *, lazy_create=None, reuse=None, register_inputs=None, register_outputs=None, simple_output=None, **config):
        """
        Inputs:
            name: Path, name of model.
            inputs: tf.Tensor | dict of str: tf.Tensor|dict|Graph
                case tf.Tensor:
                    add NodeKeys.INPUT: tf.Tensor
                case name: tf.Tensor:
                    add name: tf.Tensor to _inputs
                case name: dict
                    add name: tf.placeholder with dict['shape'], dict['type]
                case name: dict
                    add name: Graph.as_tensor()
            child_models: dict of str: Model|function
        """
        super().__init__(name, lazy_create=lazy_create, reuse=reuse, register_inputs=register_inputs,
                         register_outputs=register_outputs, simple_output=simple_output, **config)
        self._created = False
        self._scope = None
        self.inputs = self._inputs_standardization(inputs)
        self._child_models = child_models
        if not self.param('lazy_create'):
            self._construct()
        self.register_main_task(self.apply)

    @classmethod
    def _default_config(cls):
        from dxpy.collections.dicts import combine_dicts
        cfg = {
            'lazy_create': False,
            'reuse': False,
            'register_inputs': True,
            'register_outputs': True,
            'simple_output': True,
            'no_new_output_for_none_feeds': True,
            'register_output_with_prefix': True
        }
        return combine_dicts(cfg, super()._default_config())

    @classmethod
    def _default_inputs(cls):
        return dict()

    def _post_create(self):
        pass

    def _pre_kernel_pre_inputs(self):
        pass

    def _pre_kernel_post_inputs(self):
        """
        Function hook before kernel of during create. Useful to create child models.
        """
        pass

    def _post_kernel_pre_outputs(self):
        pass

    def _post_kernel_post_outputs(self):
        pass

    def _post_create(self):
        pass

    def _kernel(self, feeds):
        raise NotImplementedError

    def apply(self, feeds=None):
        if not self._created:
            self.inputs = self._inputs_standardization(feeds)
            self._construct()
            result = self.outputs
        else:
            if feeds is None:
                result = self.outputs
            else:
                with tf.variable_scope(self._variable_scope, reuse=True):
                    inputs = self._inputs_standardization(feeds)
                    result = self._outputs_standardization(
                        self._kernel(inputs))
        return self._simplified_output(result)

    def register_child_model(self, name, model):
        self._child_models[name] = model
        self.register_node('child_model/{}'.format(name), model)

    def child_model(self, key):
        return self._child_models.get(key)

    def __create_non_tensor_inputs(self):
        from .tensor import PlaceHolder
        with tf.name_scope('inputs'):
            inputs = self._inputs_standardization()
            for n in inputs:
                if isinstance(inputs[n], tf.Tensor):
                    self.register_node(n, inputs[n])
                else:
                    if isinstance(inputs[n], PlaceHolder):
                        shape = inputs[n].shape
                        dtype = inputs[n].dtype
                    else:
                        shape = inputs[n]['shape']
                        dtype = tf.float32
                    inputs[n] = self.create_placeholder_node(
                        tf.float32, inputs[n]['shape'], n)
                    self.inputs[n] = inputs[n]

    def __create_non_model_child_models(self):
        if self._child_models is None:
            self._child_models = dict()
            return
        if not isinstance(self._child_models, dict):
            if isinstance(self._child_models, Model):
                self._child_models = {NodeKeys.CHILD_MODEL: self._child_models}
            else:
                self._child_models = {
                    NodeKeys.CHILD_MODEL:  self._child_models()}
            return
        for n in self._child_models:
            if not isinstance(self._child_models[n], Model):
                self._child_models[n] = self._child_models[n]()

    def __register_inputs(self):
        if self.param('register_inputs'):
            for n in self.inputs:
                self.register_node('inputs/{}'.format(n), self.inputs[n])

    def __register_outputs(self):
        if self.param('register_outputs'):
            for n in self.outputs:
                if self.param('register_output_with_prefix'):
                    output_key = 'outputs/{}'.format(n)
                else:
                    output_key = n
                self.register_node(output_key, self.outputs[n])
                left_out_keys = [NodeKeys.MAIN,
                                 NodeKeys.LOSS, NodeKeys.INFERENCE]
                if n in left_out_keys:
                    self.register_node(n, self.outputs[n])

    def __create(self):
        if self._created:
            raise ValueError(
                "Model {} is created. Can not recreate.".format(self.name))
        assert self._scope is None
        with tf.variable_scope(self._variable_scope, reuse=False) as scope:
            self._scope = scope
            self._pre_kernel_pre_inputs()
            self.__create_non_tensor_inputs()
            self.__register_inputs()
            self.__create_non_model_child_models()
            self._pre_kernel_post_inputs()
            self.outputs = self._outputs_standardization(
                self._kernel(self.inputs))
            self._post_kernel_pre_outputs
            self.__register_outputs()
            self._post_kernel_post_outputs()
        self._created = True

    def _construct(self):
        self._post_create()
        self.__create()
        self._post_create()

    @property
    def _variable_scope(self):
        if self._scope is None:
            return self.basename
        else:
            return self._scope

    @classmethod
    def _tensor_dict_standardization(cls, tensors=None, default_key=None):
        from .tensor import PlaceHolder
        if tensors is None:
            return dict()
        if isinstance(tensors, (tf.Tensor, PlaceHolder)):
            return {default_key: tensors}
        result = dict()
        for n in tensors:
            if tensors[n] is not None:
                result[n] = tensors[n]
        return result

    def _inputs_standardization(self, inputs=None):
        result = self._default_inputs()
        if hasattr(self, 'inputs'):
            result.update(self.inputs)
        result.update(self._tensor_dict_standardization(
            inputs, NodeKeys.INPUT))
        return result

    def _outputs_standardization(self, outputs):
        result = dict()
        result.update(self._tensor_dict_standardization(
            outputs, NodeKeys.MAIN))
        return result

    def _simplified_output(self, results):
        if self.param('simple_output') and len(results) == 1 and list(results.keys())[0] == NodeKeys.MAIN:
            return results[NodeKeys.MAIN]
        return results


models = dict()


def register_model(key, model):
    if not isinstance(model, Model):
        raise TypeError("Only Model is supported, got {}.".format(type(model)))
    if key in models:
        raise ValueError("Key {} already exists.".format(key))
    models[key] = model


def load_model(key):
    return models.get(key)

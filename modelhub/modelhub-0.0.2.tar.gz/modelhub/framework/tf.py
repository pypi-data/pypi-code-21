# -*- coding: utf-8 -*-
"""
Example

class Model(TFBaseModel):
    model_name="language_detect"
"""

from .base import BaseModel
from abc import abstractproperty
from functools import partial
from modelhub.core.utils import cached_property
# from modelhub.core.models import Model


class TFBaseModel(BaseModel):
    TYPE = "TF"

    @abstractproperty
    def model_name(self):
        raise NotImplementedError

    @cached_property
    def default_schema_name(self):
        import tensorflow as tf
        return tf.saved_model.signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY

    def __init__(self, hostport, model_name=None, timeout_seconds=5, **kwargs):
        if model_name is not None:
            self.model_name = model_name
        self.timeout_seconds = timeout_seconds
        from tensorflow_serving.apis import predict_pb2
        from tensorflow.python.framework import tensor_util
        self.PredictRequest = predict_pb2.PredictRequest
        self.tensor_util = tensor_util

        self._hostport = hostport

        import grpc
        from tensorflow_serving.apis import prediction_service_pb2
        channel = grpc.insecure_channel(self._hostport)
        self.stub = prediction_service_pb2.PredictionServiceStub(channel)
        # self._version = Model.get(self.model_name).latest_version

        super().__init__(**kwargs)

    def _build_requests(self, inputs, schema):
        request = self.PredictRequest()
        request.model_spec.name = self.model_name

        if schema:
            request.model_spec.signature_name = schema
        # else signature_name="serve_default"

        for key, value in inputs.items():
            request.inputs[key].CopyFrom(self.tensor_util.make_tensor_proto(value))
        return request

    def _parse_result(self, response):
        return {key: self.tensor_util.MakeNdarray(tensor) for key, tensor in response.outputs.items()}

    def _predict_sync(self, inputs, schema=None):
        self.log_info("send %s", inputs)
        request = self._build_request(inputs)
        response = self.stub.Predict(request, self.timeout_seconds)
        result = self._parse_result(response)
        self.log_info("recv %s", result)
        return result

    def _callback(self, future, callback, inputs):
        parsed_outputs = self._get_parsed_outputs_from_future(future, inputs=inputs)
        self.log_info("recv %s %s", id(future), parsed_outputs)
        callback and callback(inputs, parsed_outputs)

    def _get_parsed_outputs_from_future(self, future, inputs=None):
        try:
            response = future.result()
        except Exception as e:
            self.on_error(inputs, e)
            raise
        return self._parse_result(response)

    def on_error(self, inputs, exception):
        self.log_error("Error happended for inputs:", extra=(inputs, "\n", exception))

    def _predict_async(self, inputs, callback=None, schema=None):
        request = self._build_requests(inputs, schema)
        future = self.stub.Predict.future(request, self.timeout_seconds)
        self.log_info("send %s %s", id(future), inputs)
        if callback is not None or self.verbose:
            callback = partial(self._callback, callback=callback, inputs=inputs)
            future.add_done_callback(callback)

        return future

    def is_ready(self):
        return True

    def run(self, data):
        """
        data should be something like
        [{
            "input1":value,
            "input2":value
        },{
            "input1":value2,
            "input2":value2,
        }]

        """
        data = self._input_maybe_list(data)
        futures = []
        for item in data:
            schema = item.pop("schema", None)
            self.validate_input_data(item)
            one_item_inputs = self._pack_data(self.preprocess(item))
            futures.append(self._predict_async(one_item_inputs, schema=schema))
        results = [
            self.postprocess(self._unpack_data(self._get_parsed_outputs_from_future(future)))
            for future in futures
        ]
        return results

    def run_model(self):
        pass

    def _input_maybe_list(self, data):
        if isinstance(data, dict):
            data = [data]
        return data

    def run_batch(self, input_generator):
        pass

    def _pack_data(self, data):
        """
        data -> {
            "input1":value,
            "input2":value
        }
        return -> {
            "input1":[value],
            "input2":[value],
        }
        """
        return {
            k: [v]
            for k, v in data.items()
        }

    def _unpack_data(self, outputs):
        """
        outputs -> {
            "result1":[value]
        }
        return -> {
            "result1":value
        }
        """
        return {
            k: v[0]
            for k, v in outputs.items()
        }

    def validate_input_data(self, data):
        pass

    def api_schema(self):
        return {}

    def _schema_to_docstring(self, schema):
        # TODO
        return schema

    def docstring(self):
        import yaml
        return yaml.dump(self._schema_to_docstring(self.api_schema()))

    def preprocess(self, item):
        """
        item -> {
            "input1":value,
            "input2":value
        }
        """
        return item

    def postprocess(self, tf_output):
        """
        tf_output -> {
            "output1":value,
            "output2":value
        }
        """
        return tf_output

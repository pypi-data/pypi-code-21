"""Python wrappers around TensorFlow ops.

This file is MACHINE GENERATED! Do not edit.
Original C++ source file: pwl_indexing_calibrator_py_wrapper.cc
"""

import collections as _collections

from tensorflow.python.eager import execute as _execute
from tensorflow.python.eager import context as _context
from tensorflow.python.eager import core as _core
from tensorflow.python.framework import dtypes as _dtypes
from tensorflow.python.framework import tensor_shape as _tensor_shape

from tensorflow.core.framework import op_def_pb2 as _op_def_pb2
# Needed to trigger the call to _set_call_cpp_shape_fn.
from tensorflow.python.framework import common_shapes as _common_shapes
from tensorflow.python.framework import op_def_registry as _op_def_registry
from tensorflow.python.framework import ops as _ops
from tensorflow.python.framework import op_def_library as _op_def_library


def pwl_indexing_calibrator(input, kp_inputs, name=None):
  r"""Returns tensor representing interpolation weights in a piecewise linear

  function. If using a large number of keypoints, try PwlIndexingCalibratorSparse.

  Notice that in this version the keypoints inputs (given by kp_inputs) is kept
  fixed by forcing its gradient to be always 0. FutureWork: allow kp_inputs to
  also be optimized, by providing a gradient.

  Inputs
    input: uncalibrated weights, `[batch_size]`
    kp_input: keypoints' input weights, can be initialized with the
              pwl_calibrator_initialize_input_keypoints op. `[num_keypoints]`

  Outputs
    weights: Interpolation weights for a piecewise linear function. Its shape is
      `[batch_size, num_keypoints]`. The dot product of this and the keypoints
      output will give the calibrated value.

  Args:
    input: A `Tensor`. Must be one of the following types: `float32`, `float64`.
    kp_inputs: A `Tensor`. Must have the same type as `input`.
    name: A name for the operation (optional).

  Returns:
    A `Tensor`. Has the same type as `input`.
  """
  _ctx = _context.context()
  if _ctx.in_graph_mode():
    _, _, _op = _op_def_lib._apply_op_helper(
        "PwlIndexingCalibrator", input=input, kp_inputs=kp_inputs, name=name)
    _result = _op.outputs[:]
    _inputs_flat = _op.inputs
    _attrs = ("Dtype", _op.get_attr("Dtype"))
  else:
    _attr_Dtype, _inputs_Dtype = _execute.args_to_matching_eager([input, kp_inputs], _ctx, _dtypes.float32)
    (input, kp_inputs) = _inputs_Dtype
    _attr_Dtype = _attr_Dtype.as_datatype_enum
    _inputs_flat = [input, kp_inputs]
    _attrs = ("Dtype", _attr_Dtype)
    _result = _execute.execute(b"PwlIndexingCalibrator", 1,
                               inputs=_inputs_flat, attrs=_attrs, ctx=_ctx,
                               name=name)
  _execute.record_gradient(
      "PwlIndexingCalibrator", _inputs_flat, _attrs, _result, name)
  _result, = _result
  return _result

_ops.RegisterShape("PwlIndexingCalibrator")(None)


_pwl_indexing_calibrator_gradient_outputs = ["grad_wrt_input",
                                            "grad_wrt_kp_inputs"]
_PwlIndexingCalibratorGradientOutput = _collections.namedtuple(
    "PwlIndexingCalibratorGradient",
    _pwl_indexing_calibrator_gradient_outputs)


def pwl_indexing_calibrator_gradient(input, kp_inputs, grad_wrt_weights, name=None):
  r"""Computes gradients of PwlIndexingCalibrator. Returns a dense gradient.

  As FutureWork we want to allow kp_inputs to be adjusted dynamically.

  Inputs
    input: uncalibrated value, `[batch_size]`.
    kp_inputs: keypoints' input weights, can be initialized with the
        pwl_calibrator_initialize_input_keypoints op, `[num_keypoints]`.
    weights_grad: Gradient with respect to the weights outputs of this operator,
        `[batch_size, num_keypoints]`.

  Outputs
    grad_wrt_input: gradient with respect to input, `[batch_size]`.
    grad_wrt_kp_inputs: gradient with respect to the kp_inputs. This is fixed in 0
        because (for now) the keypoints inputs are fixed, `[num_keypoints]`.

  Args:
    input: A `Tensor`. Must be one of the following types: `float32`, `float64`.
    kp_inputs: A `Tensor`. Must have the same type as `input`.
    grad_wrt_weights: A `Tensor`. Must have the same type as `input`.
    name: A name for the operation (optional).

  Returns:
    A tuple of `Tensor` objects (grad_wrt_input, grad_wrt_kp_inputs).

    grad_wrt_input: A `Tensor`. Has the same type as `input`.
    grad_wrt_kp_inputs: A `Tensor`. Has the same type as `input`.
  """
  _ctx = _context.context()
  if _ctx.in_graph_mode():
    _, _, _op = _op_def_lib._apply_op_helper(
        "PwlIndexingCalibratorGradient", input=input, kp_inputs=kp_inputs,
        grad_wrt_weights=grad_wrt_weights, name=name)
    _result = _op.outputs[:]
    _inputs_flat = _op.inputs
    _attrs = ("Dtype", _op.get_attr("Dtype"))
  else:
    _attr_Dtype, _inputs_Dtype = _execute.args_to_matching_eager([input, kp_inputs, grad_wrt_weights], _ctx, _dtypes.float32)
    (input, kp_inputs, grad_wrt_weights) = _inputs_Dtype
    _attr_Dtype = _attr_Dtype.as_datatype_enum
    _inputs_flat = [input, kp_inputs, grad_wrt_weights]
    _attrs = ("Dtype", _attr_Dtype)
    _result = _execute.execute(b"PwlIndexingCalibratorGradient", 2,
                               inputs=_inputs_flat, attrs=_attrs, ctx=_ctx,
                               name=name)
  _execute.record_gradient(
      "PwlIndexingCalibratorGradient", _inputs_flat, _attrs, _result, name)
  _result = _PwlIndexingCalibratorGradientOutput._make(_result)
  return _result

_ops.RegisterShape("PwlIndexingCalibratorGradient")(None)


_pwl_indexing_calibrator_sparse_outputs = ["indices", "weights"]
_PwlIndexingCalibratorSparseOutput = _collections.namedtuple(
    "PwlIndexingCalibratorSparse", _pwl_indexing_calibrator_sparse_outputs)


def pwl_indexing_calibrator_sparse(input, kp_inputs, name=None):
  r"""Returns sparse tensor representing interpolation weights in a piecewise linear

  function.

  Inputs
    input: uncalibrated weights, `[batch_size]`
    kp_input: keypoints' input weights, can be initialized with the
              pwl_calibrator_initialize_input_keypoints op. `[num_keypoints]`

  Outputs
    indices, weights: Tensors with sparse representation of interpolation weights
      for a piecewise linear function in the form of a SparseTensor. At most two
      weights will be set per uncalibrated value given. This can be multiplied
      by the keypoints' output weights. The tensor will be shaped
      `[batch_size, num_keypoints]`.

  Args:
    input: A `Tensor`. Must be one of the following types: `float32`, `float64`.
    kp_inputs: A `Tensor`. Must have the same type as `input`.
    name: A name for the operation (optional).

  Returns:
    A tuple of `Tensor` objects (indices, weights).

    indices: A `Tensor` of type `int64`.
    weights: A `Tensor`. Has the same type as `input`.
  """
  _ctx = _context.context()
  if _ctx.in_graph_mode():
    _, _, _op = _op_def_lib._apply_op_helper(
        "PwlIndexingCalibratorSparse", input=input, kp_inputs=kp_inputs,
        name=name)
    _result = _op.outputs[:]
    _inputs_flat = _op.inputs
    _attrs = ("Dtype", _op.get_attr("Dtype"))
  else:
    _attr_Dtype, _inputs_Dtype = _execute.args_to_matching_eager([input, kp_inputs], _ctx, _dtypes.float32)
    (input, kp_inputs) = _inputs_Dtype
    _attr_Dtype = _attr_Dtype.as_datatype_enum
    _inputs_flat = [input, kp_inputs]
    _attrs = ("Dtype", _attr_Dtype)
    _result = _execute.execute(b"PwlIndexingCalibratorSparse", 2,
                               inputs=_inputs_flat, attrs=_attrs, ctx=_ctx,
                               name=name)
  _execute.record_gradient(
      "PwlIndexingCalibratorSparse", _inputs_flat, _attrs, _result, name)
  _result = _PwlIndexingCalibratorSparseOutput._make(_result)
  return _result

_ops.RegisterShape("PwlIndexingCalibratorSparse")(None)


_pwl_indexing_calibrator_sparse_gradient_outputs = ["grad_wrt_input",
                                                   "grad_wrt_kp_inputs"]
_PwlIndexingCalibratorSparseGradientOutput = _collections.namedtuple(
    "PwlIndexingCalibratorSparseGradient",
    _pwl_indexing_calibrator_sparse_gradient_outputs)


def pwl_indexing_calibrator_sparse_gradient(input, kp_inputs, indices, grad_wrt_weights, name=None):
  r"""Computes gradients of PwlIndexingCalibratorSparse. Returns (dense) gradients

  with respect to the input and to the kp_inputs.

  As FutureWork we want to allow kp_inputs to be adjusted dynamically.

  Inputs
    input: uncalibrated value, `[batch_size]`.
    kp_inputs: keypoints' input weights, can be initialized with the
        pwl_calibrator_initialize_input_keypoints op, `[num_keypoints]`.
    indices, weights_grad: indices and weights gradient (gradient
        of the loss function with respect to output weights calculated by
        PwlIndexingCalibratorSparseOp). They are the sparse representation of a
        Tensor of shape `[batch_size, num_keypoints]`.

  Outputs
    grad_wrt_input: gradient with respect to input, `[batch_size]`.
    grad_wrt_kp_inputs: gradient with respect to the kp_inputs. This is fixed in 0
        because (for now) the keypoints inputs are fixed, `[num_keypoints]`.

  Args:
    input: A `Tensor`. Must be one of the following types: `float32`, `float64`.
    kp_inputs: A `Tensor`. Must have the same type as `input`.
    indices: A `Tensor` of type `int64`.
    grad_wrt_weights: A `Tensor`. Must have the same type as `input`.
    name: A name for the operation (optional).

  Returns:
    A tuple of `Tensor` objects (grad_wrt_input, grad_wrt_kp_inputs).

    grad_wrt_input: A `Tensor`. Has the same type as `input`.
    grad_wrt_kp_inputs: A `Tensor`. Has the same type as `input`.
  """
  _ctx = _context.context()
  if _ctx.in_graph_mode():
    _, _, _op = _op_def_lib._apply_op_helper(
        "PwlIndexingCalibratorSparseGradient", input=input,
        kp_inputs=kp_inputs, indices=indices,
        grad_wrt_weights=grad_wrt_weights, name=name)
    _result = _op.outputs[:]
    _inputs_flat = _op.inputs
    _attrs = ("Dtype", _op.get_attr("Dtype"))
  else:
    _attr_Dtype, _inputs_Dtype = _execute.args_to_matching_eager([input, kp_inputs, grad_wrt_weights], _ctx, _dtypes.float32)
    (input, kp_inputs, grad_wrt_weights) = _inputs_Dtype
    _attr_Dtype = _attr_Dtype.as_datatype_enum
    indices = _ops.convert_to_tensor(indices, _dtypes.int64)
    _inputs_flat = [input, kp_inputs, indices, grad_wrt_weights]
    _attrs = ("Dtype", _attr_Dtype)
    _result = _execute.execute(b"PwlIndexingCalibratorSparseGradient", 2,
                               inputs=_inputs_flat, attrs=_attrs, ctx=_ctx,
                               name=name)
  _execute.record_gradient(
      "PwlIndexingCalibratorSparseGradient", _inputs_flat, _attrs, _result, name)
  _result = _PwlIndexingCalibratorSparseGradientOutput._make(_result)
  return _result

_ops.RegisterShape("PwlIndexingCalibratorSparseGradient")(None)

def _InitOpDefLibrary(op_list_proto_bytes):
  op_list = _op_def_pb2.OpList()
  op_list.ParseFromString(op_list_proto_bytes)
  _op_def_registry.register_op_list(op_list)
  op_def_lib = _op_def_library.OpDefLibrary()
  op_def_lib.add_op_list(op_list)
  return op_def_lib
# op {
#   name: "PwlIndexingCalibrator"
#   input_arg {
#     name: "input"
#     type_attr: "Dtype"
#   }
#   input_arg {
#     name: "kp_inputs"
#     type_attr: "Dtype"
#   }
#   output_arg {
#     name: "weights"
#     type_attr: "Dtype"
#   }
#   attr {
#     name: "Dtype"
#     type: "type"
#     default_value {
#       type: DT_FLOAT
#     }
#     allowed_values {
#       list {
#         type: DT_FLOAT
#         type: DT_DOUBLE
#       }
#     }
#   }
# }
# op {
#   name: "PwlIndexingCalibratorGradient"
#   input_arg {
#     name: "input"
#     type_attr: "Dtype"
#   }
#   input_arg {
#     name: "kp_inputs"
#     type_attr: "Dtype"
#   }
#   input_arg {
#     name: "grad_wrt_weights"
#     type_attr: "Dtype"
#   }
#   output_arg {
#     name: "grad_wrt_input"
#     type_attr: "Dtype"
#   }
#   output_arg {
#     name: "grad_wrt_kp_inputs"
#     type_attr: "Dtype"
#   }
#   attr {
#     name: "Dtype"
#     type: "type"
#     default_value {
#       type: DT_FLOAT
#     }
#     allowed_values {
#       list {
#         type: DT_FLOAT
#         type: DT_DOUBLE
#       }
#     }
#   }
# }
# op {
#   name: "PwlIndexingCalibratorSparse"
#   input_arg {
#     name: "input"
#     type_attr: "Dtype"
#   }
#   input_arg {
#     name: "kp_inputs"
#     type_attr: "Dtype"
#   }
#   output_arg {
#     name: "indices"
#     type: DT_INT64
#   }
#   output_arg {
#     name: "weights"
#     type_attr: "Dtype"
#   }
#   attr {
#     name: "Dtype"
#     type: "type"
#     default_value {
#       type: DT_FLOAT
#     }
#     allowed_values {
#       list {
#         type: DT_FLOAT
#         type: DT_DOUBLE
#       }
#     }
#   }
# }
# op {
#   name: "PwlIndexingCalibratorSparseGradient"
#   input_arg {
#     name: "input"
#     type_attr: "Dtype"
#   }
#   input_arg {
#     name: "kp_inputs"
#     type_attr: "Dtype"
#   }
#   input_arg {
#     name: "indices"
#     type: DT_INT64
#   }
#   input_arg {
#     name: "grad_wrt_weights"
#     type_attr: "Dtype"
#   }
#   output_arg {
#     name: "grad_wrt_input"
#     type_attr: "Dtype"
#   }
#   output_arg {
#     name: "grad_wrt_kp_inputs"
#     type_attr: "Dtype"
#   }
#   attr {
#     name: "Dtype"
#     type: "type"
#     default_value {
#       type: DT_FLOAT
#     }
#     allowed_values {
#       list {
#         type: DT_FLOAT
#         type: DT_DOUBLE
#       }
#     }
#   }
# }
_op_def_lib = _InitOpDefLibrary(b"\nh\n\025PwlIndexingCalibrator\022\016\n\005input\"\005Dtype\022\022\n\tkp_inputs\"\005Dtype\032\020\n\007weights\"\005Dtype\"\031\n\005Dtype\022\004type\032\0020\001:\006\n\0042\002\001\002\n\257\001\n\035PwlIndexingCalibratorGradient\022\016\n\005input\"\005Dtype\022\022\n\tkp_inputs\"\005Dtype\022\031\n\020grad_wrt_weights\"\005Dtype\032\027\n\016grad_wrt_input\"\005Dtype\032\033\n\022grad_wrt_kp_inputs\"\005Dtype\"\031\n\005Dtype\022\004type\032\0020\001:\006\n\0042\002\001\002\n{\n\033PwlIndexingCalibratorSparse\022\016\n\005input\"\005Dtype\022\022\n\tkp_inputs\"\005Dtype\032\013\n\007indices\030\t\032\020\n\007weights\"\005Dtype\"\031\n\005Dtype\022\004type\032\0020\001:\006\n\0042\002\001\002\n\302\001\n#PwlIndexingCalibratorSparseGradient\022\016\n\005input\"\005Dtype\022\022\n\tkp_inputs\"\005Dtype\022\013\n\007indices\030\t\022\031\n\020grad_wrt_weights\"\005Dtype\032\027\n\016grad_wrt_input\"\005Dtype\032\033\n\022grad_wrt_kp_inputs\"\005Dtype\"\031\n\005Dtype\022\004type\032\0020\001:\006\n\0042\002\001\002")

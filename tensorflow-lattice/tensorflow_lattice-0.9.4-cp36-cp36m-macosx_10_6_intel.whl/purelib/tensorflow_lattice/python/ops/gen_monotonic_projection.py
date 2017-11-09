"""Python wrappers around TensorFlow ops.

This file is MACHINE GENERATED! Do not edit.
Original C++ source file: monotonic_projection_py_wrapper.cc
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


def monotonic_projection(values, increasing, name=None):
  r"""Returns a not-strict monotonic projection of the vector.

  The returned vector is of the same size as the input and values (optionally)
  changed to make them monotonically, minimizing the sum of the square distance
  to the original values.

  This is part of the set of ops that support monotonicity in piecewise-linear
  calibration.

  Note that the gradient is undefined for this function.

    values: `Tensor` with values to be made monotonic.
    increasing: Defines if projection it to monotonic increasing values
      or to monotonic decreasing ones.

    monotonic: output `Tensor` with values made monotonic.

  Args:
    values: A `Tensor`. Must be one of the following types: `float32`, `float64`.
    increasing: A `Tensor` of type `bool`.
    name: A name for the operation (optional).

  Returns:
    A `Tensor`. Has the same type as `values`.
  """
  _ctx = _context.context()
  if _ctx.in_graph_mode():
    _, _, _op = _op_def_lib._apply_op_helper(
        "MonotonicProjection", values=values, increasing=increasing,
        name=name)
    _result = _op.outputs[:]
    _inputs_flat = _op.inputs
    _attrs = ("Dtype", _op.get_attr("Dtype"))
  else:
    _attr_Dtype, (values,) = _execute.args_to_matching_eager([values], _ctx, _dtypes.float32)
    _attr_Dtype = _attr_Dtype.as_datatype_enum
    increasing = _ops.convert_to_tensor(increasing, _dtypes.bool)
    _inputs_flat = [values, increasing]
    _attrs = ("Dtype", _attr_Dtype)
    _result = _execute.execute(b"MonotonicProjection", 1, inputs=_inputs_flat,
                               attrs=_attrs, ctx=_ctx, name=name)
  _execute.record_gradient(
      "MonotonicProjection", _inputs_flat, _attrs, _result, name)
  _result, = _result
  return _result

_ops.RegisterShape("MonotonicProjection")(None)

def _InitOpDefLibrary(op_list_proto_bytes):
  op_list = _op_def_pb2.OpList()
  op_list.ParseFromString(op_list_proto_bytes)
  _op_def_registry.register_op_list(op_list)
  op_def_lib = _op_def_library.OpDefLibrary()
  op_def_lib.add_op_list(op_list)
  return op_def_lib
# op {
#   name: "MonotonicProjection"
#   input_arg {
#     name: "values"
#     type_attr: "Dtype"
#   }
#   input_arg {
#     name: "increasing"
#     type: DT_BOOL
#   }
#   output_arg {
#     name: "monotonic"
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
_op_def_lib = _InitOpDefLibrary(b"\ne\n\023MonotonicProjection\022\017\n\006values\"\005Dtype\022\016\n\nincreasing\030\n\032\022\n\tmonotonic\"\005Dtype\"\031\n\005Dtype\022\004type\032\0020\001:\006\n\0042\002\001\002")

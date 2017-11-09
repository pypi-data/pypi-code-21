"""Python wrappers around TensorFlow ops.

This file is MACHINE GENERATED! Do not edit.
Original C++ source file: monotone_lattice_py_wrapper.cc
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


def monotone_lattice(lattice_params, is_monotone=[], lattice_sizes=[], tolerance=1e-07, max_iter=1000, name=None):
  r"""Returns a projected lattice parameters onto the monotonicity constraints.

  Monotonicity constraints are specified is_monotone. If is_monotone[k] == True,
  then the kth input has a non-decreasing monotonicity, otherwise there will be no
  constraints.

  This operator uses an iterative algorithm, Alternating Direction Method of
  Multipliers (ADMM) method, to find the projection, so tolerance and max_iter can
  be used to control the accuracy vs. the time spent trade-offs in the ADMM
  method.

  Inputs
    lattice_params: 2D tensor, `[number of outputs, number of parameters]`

  Params
    is_monotone: 1D bool tensor that contains whether the kth dimension should be
    monotonic.
    lattice_sizes: 1D int tensor that contains a lattice size per each dimension,
    [m_0, ..., m_{d - 1}].
    tolerance: The tolerance in ||true projection - projection|| in the ADMM
    method.
    max_iter: Maximum number of iterations in the ADMM method.

  Outputs
    projected_lattice_params: 2D tensor,
    `[number of outputs, number of parameters]`, that contains the projected
    parameters.

  Args:
    lattice_params: A `Tensor`. Must be one of the following types: `float32`, `float64`.
    is_monotone: An optional list of `bools`. Defaults to `[]`.
    lattice_sizes: An optional list of `ints`. Defaults to `[]`.
    tolerance: An optional `float`. Defaults to `1e-07`.
    max_iter: An optional `int`. Defaults to `1000`.
    name: A name for the operation (optional).

  Returns:
    A `Tensor`. Has the same type as `lattice_params`.
  """
  if is_monotone is None:
    is_monotone = []
  if not isinstance(is_monotone, (list, tuple)):
    raise TypeError(
        "Expected list for 'is_monotone' argument to "
        "'monotone_lattice' Op, not %r." % is_monotone)
  is_monotone = [_execute.make_bool(_b, "is_monotone") for _b in is_monotone]
  if lattice_sizes is None:
    lattice_sizes = []
  if not isinstance(lattice_sizes, (list, tuple)):
    raise TypeError(
        "Expected list for 'lattice_sizes' argument to "
        "'monotone_lattice' Op, not %r." % lattice_sizes)
  lattice_sizes = [_execute.make_int(_i, "lattice_sizes") for _i in lattice_sizes]
  if tolerance is None:
    tolerance = 1e-07
  tolerance = _execute.make_float(tolerance, "tolerance")
  if max_iter is None:
    max_iter = 1000
  max_iter = _execute.make_int(max_iter, "max_iter")
  _ctx = _context.context()
  if _ctx.in_graph_mode():
    _, _, _op = _op_def_lib._apply_op_helper(
        "MonotoneLattice", lattice_params=lattice_params,
        is_monotone=is_monotone, lattice_sizes=lattice_sizes,
        tolerance=tolerance, max_iter=max_iter, name=name)
    _result = _op.outputs[:]
    _inputs_flat = _op.inputs
    _attrs = ("Dtype", _op.get_attr("Dtype"), "is_monotone",
              _op.get_attr("is_monotone"), "lattice_sizes",
              _op.get_attr("lattice_sizes"), "tolerance",
              _op.get_attr("tolerance"), "max_iter", _op.get_attr("max_iter"))
  else:
    _attr_Dtype, (lattice_params,) = _execute.args_to_matching_eager([lattice_params], _ctx, _dtypes.float32)
    _attr_Dtype = _attr_Dtype.as_datatype_enum
    _inputs_flat = [lattice_params]
    _attrs = ("Dtype", _attr_Dtype, "is_monotone", is_monotone,
              "lattice_sizes", lattice_sizes, "tolerance", tolerance,
              "max_iter", max_iter)
    _result = _execute.execute(b"MonotoneLattice", 1, inputs=_inputs_flat,
                               attrs=_attrs, ctx=_ctx, name=name)
  _execute.record_gradient(
      "MonotoneLattice", _inputs_flat, _attrs, _result, name)
  _result, = _result
  return _result

def _InitOpDefLibrary(op_list_proto_bytes):
  op_list = _op_def_pb2.OpList()
  op_list.ParseFromString(op_list_proto_bytes)
  _op_def_registry.register_op_list(op_list)
  op_def_lib = _op_def_library.OpDefLibrary()
  op_def_lib.add_op_list(op_list)
  return op_def_lib
# op {
#   name: "MonotoneLattice"
#   input_arg {
#     name: "lattice_params"
#     type_attr: "Dtype"
#   }
#   output_arg {
#     name: "projected_lattice_params"
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
#   attr {
#     name: "is_monotone"
#     type: "list(bool)"
#     default_value {
#       list {
#       }
#     }
#   }
#   attr {
#     name: "lattice_sizes"
#     type: "list(int)"
#     default_value {
#       list {
#       }
#     }
#   }
#   attr {
#     name: "tolerance"
#     type: "float"
#     default_value {
#       f: 1e-07
#     }
#   }
#   attr {
#     name: "max_iter"
#     type: "int"
#     default_value {
#       i: 1000
#     }
#   }
# }
_op_def_lib = _InitOpDefLibrary(b"\n\330\001\n\017MonotoneLattice\022\027\n\016lattice_params\"\005Dtype\032!\n\030projected_lattice_params\"\005Dtype\"\031\n\005Dtype\022\004type\032\0020\001:\006\n\0042\002\001\002\"\035\n\013is_monotone\022\nlist(bool)\032\002\n\000\"\036\n\rlattice_sizes\022\tlist(int)\032\002\n\000\"\031\n\ttolerance\022\005float\032\005%\225\277\3263\"\024\n\010max_iter\022\003int\032\003\030\350\007")

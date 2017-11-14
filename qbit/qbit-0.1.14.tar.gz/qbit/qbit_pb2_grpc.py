import grpc
from grpc.framework.common import cardinality
from grpc.framework.interfaces.face import utilities as face_utilities

import qbit_pb2 as qbit__pb2
import qbit_pb2 as qbit__pb2
import qbit_pb2 as qbit__pb2
import qbit_pb2 as qbit__pb2
import qbit_pb2 as qbit__pb2
import qbit_pb2 as qbit__pb2
import qbit_pb2 as qbit__pb2
import qbit_pb2 as qbit__pb2
import qbit_pb2 as qbit__pb2
import qbit_pb2 as qbit__pb2
import qbit_pb2 as qbit__pb2
import qbit_pb2 as qbit__pb2
import qbit_pb2 as qbit__pb2
import qbit_pb2 as qbit__pb2
import qbit_pb2 as qbit__pb2
import qbit_pb2 as qbit__pb2
import qbit_pb2 as qbit__pb2
import qbit_pb2 as qbit__pb2
import qbit_pb2 as qbit__pb2
import google.protobuf.empty_pb2 as google_dot_protobuf_dot_empty__pb2
import qbit_pb2 as qbit__pb2
import google.protobuf.empty_pb2 as google_dot_protobuf_dot_empty__pb2
import qbit_pb2 as qbit__pb2
import google.protobuf.empty_pb2 as google_dot_protobuf_dot_empty__pb2
import qbit_pb2 as qbit__pb2
import google.protobuf.empty_pb2 as google_dot_protobuf_dot_empty__pb2
import qbit_pb2 as qbit__pb2
import google.protobuf.empty_pb2 as google_dot_protobuf_dot_empty__pb2


class QbitStub(object):

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.CompareMolecule = channel.unary_unary(
        '/qbit.services.Qbit/CompareMolecule',
        request_serializer=qbit__pb2.CompareRequest.SerializeToString,
        response_deserializer=qbit__pb2.ComparisonResult.FromString,
        )
    self.Hobo2Qubo = channel.unary_unary(
        '/qbit.services.Qbit/Hobo2Qubo',
        request_serializer=qbit__pb2.BinaryPolynomial.SerializeToString,
        response_deserializer=qbit__pb2.BinaryPolynomial.FromString,
        )
    self.SolveQubo = channel.unary_unary(
        '/qbit.services.Qbit/SolveQubo',
        request_serializer=qbit__pb2.QuboRequest.SerializeToString,
        response_deserializer=qbit__pb2.QuboResponse.FromString,
        )
    self.Knapsack = channel.unary_unary(
        '/qbit.services.Qbit/Knapsack',
        request_serializer=qbit__pb2.KnapsackRequest.SerializeToString,
        response_deserializer=qbit__pb2.KnapsackResponse.FromString,
        )
    self.MinKCutPartitioning = channel.unary_unary(
        '/qbit.services.Qbit/MinKCutPartitioning',
        request_serializer=qbit__pb2.MinKCutRequest.SerializeToString,
        response_deserializer=qbit__pb2.MinKCutResponse.FromString,
        )
    self.ListOperations = channel.unary_unary(
        '/qbit.services.Qbit/ListOperations',
        request_serializer=qbit__pb2.ListOperationsRequest.SerializeToString,
        response_deserializer=qbit__pb2.ListOperationsResponse.FromString,
        )
    self.GetOperation = channel.unary_unary(
        '/qbit.services.Qbit/GetOperation',
        request_serializer=qbit__pb2.GetOperationRequest.SerializeToString,
        response_deserializer=qbit__pb2.Operation.FromString,
        )
    self.GetOperationDetail = channel.unary_unary(
        '/qbit.services.Qbit/GetOperationDetail',
        request_serializer=qbit__pb2.GetOperationRequest.SerializeToString,
        response_deserializer=qbit__pb2.OperationDetail.FromString,
        )
    self.GetOperationToWorkOn = channel.unary_unary(
        '/qbit.services.Qbit/GetOperationToWorkOn',
        request_serializer=qbit__pb2.GetOperationToWorkOnRequest.SerializeToString,
        response_deserializer=qbit__pb2.OperationDetail.FromString,
        )
    self.PutOperationBackToQueue = channel.unary_unary(
        '/qbit.services.Qbit/PutOperationBackToQueue',
        request_serializer=qbit__pb2.GetOperationRequest.SerializeToString,
        response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
        )
    self.CancelOperation = channel.unary_unary(
        '/qbit.services.Qbit/CancelOperation',
        request_serializer=qbit__pb2.CancelOperationRequest.SerializeToString,
        response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
        )
    self.CompleteOperation = channel.unary_unary(
        '/qbit.services.Qbit/CompleteOperation',
        request_serializer=qbit__pb2.CompleteOperationRequest.SerializeToString,
        response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
        )
    self.ErrorOperation = channel.unary_unary(
        '/qbit.services.Qbit/ErrorOperation',
        request_serializer=qbit__pb2.ErrorOperationRequest.SerializeToString,
        response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
        )
    self.HealthCheck = channel.unary_unary(
        '/qbit.services.Qbit/HealthCheck',
        request_serializer=qbit__pb2.HealthCheckRequest.SerializeToString,
        response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
        )


class QbitServicer(object):

  def CompareMolecule(self, request, context):
    """Compare molecules.

    With a specified solver, compare molecular similarities with a set of criterias.

    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def Hobo2Qubo(self, request, context):
    """Converts HOBO to QUBO.

    Given a Higher Order Binary Optimization (HOBO) problem, convert into
    QUBO form.

    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def SolveQubo(self, request, context):
    """Solves a QUBO.

    Given a QUBO and a solver with optionally set parameters, return a list
    of Solutions ordered by energy.

    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def Knapsack(self, request, context):
    """Solves knapsack
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def MinKCutPartitioning(self, request, context):
    """Solves MinKCutPartitioning
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def ListOperations(self, request, context):
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetOperation(self, request, context):
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetOperationDetail(self, request, context):
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetOperationToWorkOn(self, request, context):
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def PutOperationBackToQueue(self, request, context):
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def CancelOperation(self, request, context):
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def CompleteOperation(self, request, context):
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def ErrorOperation(self, request, context):
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def HealthCheck(self, request, context):
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_QbitServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'CompareMolecule': grpc.unary_unary_rpc_method_handler(
          servicer.CompareMolecule,
          request_deserializer=qbit__pb2.CompareRequest.FromString,
          response_serializer=qbit__pb2.ComparisonResult.SerializeToString,
      ),
      'Hobo2Qubo': grpc.unary_unary_rpc_method_handler(
          servicer.Hobo2Qubo,
          request_deserializer=qbit__pb2.BinaryPolynomial.FromString,
          response_serializer=qbit__pb2.BinaryPolynomial.SerializeToString,
      ),
      'SolveQubo': grpc.unary_unary_rpc_method_handler(
          servicer.SolveQubo,
          request_deserializer=qbit__pb2.QuboRequest.FromString,
          response_serializer=qbit__pb2.QuboResponse.SerializeToString,
      ),
      'Knapsack': grpc.unary_unary_rpc_method_handler(
          servicer.Knapsack,
          request_deserializer=qbit__pb2.KnapsackRequest.FromString,
          response_serializer=qbit__pb2.KnapsackResponse.SerializeToString,
      ),
      'MinKCutPartitioning': grpc.unary_unary_rpc_method_handler(
          servicer.MinKCutPartitioning,
          request_deserializer=qbit__pb2.MinKCutRequest.FromString,
          response_serializer=qbit__pb2.MinKCutResponse.SerializeToString,
      ),
      'ListOperations': grpc.unary_unary_rpc_method_handler(
          servicer.ListOperations,
          request_deserializer=qbit__pb2.ListOperationsRequest.FromString,
          response_serializer=qbit__pb2.ListOperationsResponse.SerializeToString,
      ),
      'GetOperation': grpc.unary_unary_rpc_method_handler(
          servicer.GetOperation,
          request_deserializer=qbit__pb2.GetOperationRequest.FromString,
          response_serializer=qbit__pb2.Operation.SerializeToString,
      ),
      'GetOperationDetail': grpc.unary_unary_rpc_method_handler(
          servicer.GetOperationDetail,
          request_deserializer=qbit__pb2.GetOperationRequest.FromString,
          response_serializer=qbit__pb2.OperationDetail.SerializeToString,
      ),
      'GetOperationToWorkOn': grpc.unary_unary_rpc_method_handler(
          servicer.GetOperationToWorkOn,
          request_deserializer=qbit__pb2.GetOperationToWorkOnRequest.FromString,
          response_serializer=qbit__pb2.OperationDetail.SerializeToString,
      ),
      'PutOperationBackToQueue': grpc.unary_unary_rpc_method_handler(
          servicer.PutOperationBackToQueue,
          request_deserializer=qbit__pb2.GetOperationRequest.FromString,
          response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
      ),
      'CancelOperation': grpc.unary_unary_rpc_method_handler(
          servicer.CancelOperation,
          request_deserializer=qbit__pb2.CancelOperationRequest.FromString,
          response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
      ),
      'CompleteOperation': grpc.unary_unary_rpc_method_handler(
          servicer.CompleteOperation,
          request_deserializer=qbit__pb2.CompleteOperationRequest.FromString,
          response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
      ),
      'ErrorOperation': grpc.unary_unary_rpc_method_handler(
          servicer.ErrorOperation,
          request_deserializer=qbit__pb2.ErrorOperationRequest.FromString,
          response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
      ),
      'HealthCheck': grpc.unary_unary_rpc_method_handler(
          servicer.HealthCheck,
          request_deserializer=qbit__pb2.HealthCheckRequest.FromString,
          response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'qbit.services.Qbit', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))

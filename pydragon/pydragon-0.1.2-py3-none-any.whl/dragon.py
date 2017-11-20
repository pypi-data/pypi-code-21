import pydragon.dragon_pb2 as dragon_pb2
import pydragon.dragon_pb2_grpc as dragon_pb2_grpc
import grpc
from google.protobuf.json_format import MessageToDict


class PyDragon:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.stub = self.get_stub()

    def get_stub(self):
        channel = grpc.insecure_channel(self.host + ':' + str(self.port))
        stub = dragon_pb2_grpc.DragonServiceStub(channel)
        return stub

    def get_all_services(self):
        try:
            resp = self.stub.GetServices(dragon_pb2.GetServicesRequest())
        except grpc.RpcError as e:
            raise ConnectionError('GRPC Connection Error, {}'.format(e))
        resp_obj = MessageToDict(resp)
        if resp.response.success:
            return resp_obj['services']
        else:
            return None

    def get_all_instances(self, service_name):
        try:
            resp = self.stub.GetService(dragon_pb2.GetServiceRequest(service_name=service_name))
            # print(resp)
        except grpc.RpcError as e:
            raise ConnectionError('GRPC Connection Error, {}'.format(e))
        resp_obj = MessageToDict(resp)
        if resp.response.success and resp_obj['instances']:
            return resp_obj['instances']
        else:
            return None

    def get_instance(self, service_name):
        try:
            resp = self.stub.GetServiceLBInstance(dragon_pb2.GetServiceLBInstanceRequest(service_name=service_name))
        except grpc.RpcError as e:
            raise ConnectionError('GRPC Connection Error, {}'.format(e))
        resp_obj = MessageToDict(resp)
        if resp.response.success and resp_obj['instance']:
            return resp_obj['instance']
        else:
            return None


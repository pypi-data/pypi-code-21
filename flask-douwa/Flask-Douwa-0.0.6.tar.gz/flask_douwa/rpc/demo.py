from flask_douwa.protoparser import make_client, load_byte
from flask_douwa.rpc.generator_id import GeneratorRpc
import grpc
from flask_douwa import routes


class ProxyGetRpc(object):
    def __init__(self, host, data, name):
        self.client = make_client(load_byte(data))
        self.channel = grpc.insecure_channel(host)
        self.stub = getattr(self.client,name+"Stub")(self.channel)

    def __getattr__(self, name):
        fun = getattr(self.stub, name)
        def run(**kwargs):
            request = getattr(self.client,name+"Request")(**kwargs)
            return fun(request)._result
        return run


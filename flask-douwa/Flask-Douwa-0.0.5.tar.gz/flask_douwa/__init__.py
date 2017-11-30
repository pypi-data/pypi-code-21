from flask_douwa import routes
from flask_douwa.rpc.generator_id import GeneratorRpc
from flask_douwa.rpc.demo import ProxyGetRpc
from flask_douwa.cache import RedisCache

redis = RedisCache()


class Douwa(object):

    def __init__(self, app=None):
        self.getid = None
        access_token = list()
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        host =  app.config["GENERATORID_IP"]
        rpc_register = routes.register
        proto = rpc_register(GeneratorRpc)
        self.getid = ProxyGetRpc(host, proto[0], GeneratorRpc.name)
        redis.connect(app.config["REDIS_HOST"], app.config["REDIS_PORT"], app.config["REDIS_DB"])

    def generator_id(self):
        if self.getid:
            return self.getid.GeneratorId()
        else:
            raise Exception("没有初始化")

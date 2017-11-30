from flask_douwa.routes import rpcapi
from flask_douwa.rpc.type import *
#from hex_utils.dataformat import dataformat

class GeneratorRpc:
    package = "generator_id"
    name = "Generator"

    @rpcapi(returns=StringField)
    #@dataformat
    def GeneratorId(self):
        pass

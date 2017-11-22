import uuid
from pprint import pprint

from core import initialize
from dataclay.core.dclay_yaml import load
from core.serialization.classes import RemoteCallSerialization
from core.network.client import Client
from core.config import ConfigOptions


__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'

DATASET_NAME = "DataSet"


if __name__ == "__main__":
    # Initialization
    initialize()

    consumer_id = uuid.UUID(raw_input("Input the account UUID: "))
    contract_id = uuid.UUID(raw_input("Input the contract UUID: "))

    consumer_credential = (consumer_id,
                           "EXEC_CONSUMER".encode('utf-16-be'))

    client = Client(ConfigOptions.logicmodule_host,
                    ConfigOptions.logicmodule_port)

    babel_stubs = load(client.get_babel_stubs(consumer_credential, [contract_id]))
    pprint(babel_stubs)

    cs = RemoteCallSerialization()
    metaclass_id = babel_stubs["ExecutionClass"]["metaClassID"]
    for op_id, op_info in babel_stubs["ExecutionClass"]["operations"].iteritems():
        if op_info["operationName"] == "getPrimitiveProperty":
            operation_id = op_id
            remote_implementation = op_info["remoteImplInfo"]
            cs.return_type = op_info["returnType"]
            cs.parameter_names = op_info["parameters"]["names"]
            cs.parameter_types = op_info["parameters"]["types"]
            break

    # ToDo: Pass also the account_id and the new_session_lang to the client
    session_id = client.new_session(consumer_credential, [contract_id],
                                    [DATASET_NAME], DATASET_NAME)
    persistent_uuid = uuid.UUID(raw_input("Input the persistend UUID: "))

    ret = client.execute_implementation(session_id, operation_id, remote_implementation,
                                        persistent_uuid, metaclass_id, cs)

    print ret

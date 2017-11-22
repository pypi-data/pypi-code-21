import uuid
from pprint import pprint
from multiprocessing import Process
import signal

from gevent import signal as gsignal
import os.path
import numpy as np

import dataclay
from dataclay.class_manager.metaclass import DCLAYMetaclass
from dataclay.config import ConfigOptions
from dataclay.network.client import Client
from dclay_server import main
from dataclay.debug.javaserver import JavaServerManager
import dataclay.debug
from dataclay import initialize, debug
from dataclay.dclay_yaml import load


__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'

# NEURON DATA constants, lowercase because that's how NeuronData rulz
maxlag = 200
num_surrs = 1000
num_neurons = 100
num_secs = 10
num_bins = num_secs*1000


DCLAY_ARRAY_CLASSNAME = 'dataclay.collections.DataClayArray'
DATASET_NAME = "Dataset"


def cc_surrogate_range(block_i, block_j, spikes, correlation):
    idxrange = range(num_bins - maxlag, num_bins + maxlag + 1)
    surrs_ij = np.zeros((num_surrs, 2 * maxlag + 1))
    my_cc_surrs = np.zeros((2 * maxlag + 1, 2))

    i = 0
    for ni in block_i:
        i += 1
        print "Key", ni
        for nj in block_j:
            # break
            if ni < nj:
                print "Correlation", ni, nj
                spki = spikes.get([ni])
                spkj = spikes.get([nj])

                # cc_originals is third dimension = 0
                correlation.set(np.correlate(spki, spkj, "full")[idxrange], [ni, nj, 0])
                num_spikes_i = sum(spki)
                num_spikes_j = sum(spkj)
                for surrogate in range(num_surrs):
                    surr_i = np.zeros(num_bins)
                    surr_i[np.random.random_integers(0, num_bins - 1, num_spikes_i)] = 1
                    surr_j = np.zeros(num_bins)
                    surr_j[np.random.random_integers(0, num_bins - 1, num_spikes_j)] = 1
                    surrs_ij[surrogate, :] = np.correlate(surr_i, surr_j, "full")[idxrange]
                # save point-wise 5% and 95% values of sorted surrogate ccs
                surrs_ij_sorted = np.sort(surrs_ij, axis=0)
                my_cc_surrs[:, 0] = surrs_ij_sorted[round(num_surrs*0.95), :]
                my_cc_surrs[:, 1] = surrs_ij_sorted[round(num_surrs*0.05), :]

                # cc_surrs is third dimension = 1
                correlation.set(my_cc_surrs, [ni, nj, 1])

                # Debugging "one-shot" for fast debugging, remove for real testing
                return

if __name__ == "__main__":
    # Initialization for everyone
    initialize()

    # initialization for the Execution Environment
    p = Process(target=main, name="dataClay Server Process")
    p.daemon = True
    p.start()
    # SIGHUP is used internally by the dataClay server process
    gsignal(signal.SIGHUP, signal.SIG_IGN)

    server = JavaServerManager(server_jar=os.path.join(debug.BASE_PATH,
                                                       "ContainerTestingServer.jar"))
    # server = JavaServerManager.connect_to_preloaded()

    print "Ready to do things"
    with server:
        # Redundant because mix of user-friendly and debug paths
        consumer_credential = (uuid.UUID(server.commands["consumer_id"]),
                               server.commands["consumer_password"].encode('utf-16-be'))
        dataclay.set_credentials(server.commands["consumer_user_name"],
                                 server.commands["consumer_password"])

        contract_id = uuid.UUID(server.commands["class_contracts"][DCLAY_ARRAY_CLASSNAME])

        client = Client(ConfigOptions.logicmodule_host,
                        ConfigOptions.logicmodule_port)

        print "Retrieving Babel Stubs . . ."
        babel_stubs = load(client.get_babel_stubs(consumer_credential,
                                                  [contract_id]))
        dclay_array = babel_stubs[DCLAY_ARRAY_CLASSNAME]
        pprint(dclay_array)

        ArrayClassStub = DCLAYMetaclass.create_class_from_babel(
            "DataClayArray", dclay_array)

        # ToDo: Pass also the account_id and the new_session_lang to the client
        session_id = dataclay.new_session([contract_id], [DATASET_NAME], DATASET_NAME)

        persistend_uuid = uuid.UUID(server.commands["spikes_data_oid"])
        arr = ArrayClassStub.return_object_from_persistent_uuid(persistend_uuid, [])
        size = arr.size()
        print "Array (spikes) size:", size

        persistend_uuid = uuid.UUID(server.commands["correlation_matrix_oid"])
        mat = ArrayClassStub.return_object_from_persistent_uuid(persistend_uuid, [])
        print "Matrix (correlation output) size:", mat.size()

        blocks = [range(0, size//2), range(size//2, size)]
        for block_i in blocks:
            for block_j in blocks:
                cc_surrogate_range(block_i, block_j, arr, mat)

        # wait for everything to finish

        # ok, no problem 'cause everything is sequential at the moment
        server.send_command("store")

    print "Finished"

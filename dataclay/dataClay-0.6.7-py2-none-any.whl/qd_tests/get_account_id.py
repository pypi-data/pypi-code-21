from dataclay.conf import settings
# from dataclay.core.network.client import Client
from dataclay.core import initialize
from dataclay.core.network.exceptions import RemoteException
from dataclay.core.constants import error_codes
from communication.grpc.clients.ee_client import EEClient

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'

if __name__ == "__main__":
    initialize()

    # Load the connection settings
    settings.load_connection("./configtests/client.properties")

    c = EEClient("127.0.0.1", 1034)
    print c.get_account_id("admin")

    # This should fail
    try:
        print c.get_account_id("admin-not-exist")
    except RemoteException as e:
        print "Okay, received the following RemoteException (expected?):\n --> %s" % e
        print "Code for ACCOUNT_NOT_EXIST: %s" % error_codes.ACCOUNT_NOT_EXIST

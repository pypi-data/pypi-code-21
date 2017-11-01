from random import getrandbits
from datetime import datetime, timedelta

import globus_sdk
from globus_sdk.exc import TransferAPIError
from tests.framework.constants import (GO_EP1_ID,
                                       SDKTESTER1A_NATIVE1_TRANSFER_RT,
                                       SDKTESTER2B_NATIVE1_TRANSFER_RT)
from tests.framework.capturedio_testcase import CapturedIOTestCase
from tests.framework.tools import get_client_data


def cleanSharing(tc):
        """
        Cleans out any files in ~/.globus/sharing/ on go#ep1 older than an hour
        TODO: remove this once deleting shared directories does full cleanup
        """
        path = "~/.globus/sharing/"
        hour_ago = datetime.utcnow() - timedelta(hours=1)
        filter_string = (
            "last_modified:," + hour_ago.strftime("%Y-%m-%d %H:%M:%S"))
        try:
            old_files = tc.operation_ls(
                GO_EP1_ID, path=path, filter=filter_string)
        except TransferAPIError:  # no .globus dir exists
            return

        ddata = globus_sdk.DeleteData(tc, GO_EP1_ID, notify_on_fail=False,
                                      notify_on_succeeded=False)
        for item in old_files:
            ddata.add_item(path + item["name"])

        if len(ddata["DATA"]):
            tc.submit_delete(ddata)


class TransferClientTestCase(CapturedIOTestCase):
    """
    Class that has general setUp and tearDown methods for all classes
    that tests the transfer client.
    """

    __test__ = False  # prevents base class from trying to run tests

    @classmethod
    def setUpClass(self):
        """
        Does an auth flow to create an authorized client for
        sdktester1a and sdktester2b
        Cleans out any old sharing files before running tests
        """
        ac = globus_sdk.NativeAppAuthClient(
            client_id=get_client_data()["native_app_client1"]["id"])

        authorizer1 = globus_sdk.RefreshTokenAuthorizer(
            SDKTESTER1A_NATIVE1_TRANSFER_RT, ac)
        self.tc = globus_sdk.TransferClient(authorizer=authorizer1)

        authorizer2 = globus_sdk.RefreshTokenAuthorizer(
            SDKTESTER2B_NATIVE1_TRANSFER_RT, ac)
        self.tc2 = globus_sdk.TransferClient(authorizer=authorizer2)

        cleanSharing(self.tc)

    def setUp(self):
        """
        Creates a list for tracking cleanup of assets created during testing
        Sets up a test endpoint
        """
        super(TransferClientTestCase, self).setUp()
        # list of dicts, each containing a function and a list of args
        # to pass to that function s.t. calling f(*args) cleans an asset
        self.asset_cleanup = []

        # test endpoint, uses 128 bits of randomness to prevent collision
        data = {"display_name": "SDK Test Endpoint-" + str(getrandbits(128)),
                "description": "Endpoint for testing the SDK"}
        r = self.tc.create_endpoint(data)
        self.test_ep_id = r["id"]
        self.asset_cleanup.append({"function": self.tc.delete_endpoint,
                                   "args": [r["id"]],
                                   "name": "test_ep"})  # for ease of removal

    def tearDown(self):
        """
        Parses created_assets to destroy all assets created during testing
        """
        super(TransferClientTestCase, self).tearDown()
        # call the cleanup functions with the arguments they were given
        for cleanup in self.asset_cleanup:
            cleanup["function"](*cleanup["args"])

    def deleteHelper(self, ep_id, path):
        """
        Helper function for cleanup. Deletes by path and endpoint,
        """
        kwargs = {"notify_on_succeeded": False}  # prevent email spam
        ddata = globus_sdk.DeleteData(self.tc, ep_id,
                                      label="deleteHelper",
                                      recursive=True, **kwargs)
        ddata.add_item(path)
        self.tc.submit_delete(ddata)

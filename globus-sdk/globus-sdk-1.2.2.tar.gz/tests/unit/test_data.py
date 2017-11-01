import globus_sdk

from tests.framework import (CapturedIOTestCase, get_client_data,
                             SDKTESTER1A_NATIVE1_TRANSFER_RT,
                             GO_EP1_ID, GO_EP2_ID)


class DataTests(CapturedIOTestCase):

    @classmethod
    def setUpClass(self):
        """
        Sets up transfer client for creating Data objects
        """
        ac = globus_sdk.NativeAppAuthClient(
            client_id=get_client_data()["native_app_client1"]["id"])
        authorizer = globus_sdk.RefreshTokenAuthorizer(
            SDKTESTER1A_NATIVE1_TRANSFER_RT, ac)
        self.tc = globus_sdk.TransferClient(authorizer=authorizer)

    def setUp(self):
        """
        Creates a TransferData objects and a DeleteData object for testing
        """
        super(DataTests, self).setUp()
        self.tdata = globus_sdk.TransferData(self.tc, GO_EP1_ID, GO_EP2_ID)
        self.ddata = globus_sdk.DeleteData(self.tc, GO_EP1_ID)

    def test_tranfer_init(self):
        """
        Creates TransferData objects with and without parameters,
        Verifies TransferData field initialization
        """
        # default init
        default_tdata = globus_sdk.TransferData(self.tc, GO_EP1_ID, GO_EP2_ID)
        self.assertEqual(default_tdata["DATA_TYPE"], "transfer")
        self.assertEqual(default_tdata["source_endpoint"], GO_EP1_ID)
        self.assertEqual(default_tdata["destination_endpoint"], GO_EP2_ID)
        self.assertIn("submission_id", default_tdata)
        self.assertIn("DATA", default_tdata)
        self.assertEqual(len(default_tdata["DATA"]), 0)

        # init with params
        label = "label"
        params = {"param1": "value1", "param2": "value2"}
        param_tdata = globus_sdk.TransferData(self.tc,
                                              GO_EP1_ID, GO_EP2_ID,
                                              label=label,
                                              sync_level="exists",
                                              **params)
        self.assertEqual(param_tdata["label"], label)
        # sync_level of "exists" should be converted to 0
        self.assertEqual(param_tdata["sync_level"], 0)
        for par in params:
            self.assertEqual(param_tdata[par], params[par])

    def test_transfer_add_item(self):
        """
        Adds two items to TransferData, verifies results
        """
        # add item
        source_path = "source/path/"
        dest_path = "dest/path/"
        self.tdata.add_item(source_path, dest_path)
        # verify results
        self.assertEqual(len(self.tdata["DATA"]), 1)
        data = self.tdata["DATA"][0]
        self.assertEqual(data["DATA_TYPE"], "transfer_item")
        self.assertEqual(data["source_path"], source_path)
        self.assertEqual(data["destination_path"], dest_path)
        self.assertEqual(data["recursive"], False)

        # add recursive item
        self.tdata.add_item(source_path, dest_path, recursive=True)
        # verify results
        self.assertEqual(len(self.tdata["DATA"]), 2)
        r_data = self.tdata["DATA"][1]
        self.assertEqual(r_data["DATA_TYPE"], "transfer_item")
        self.assertEqual(r_data["source_path"], source_path)
        self.assertEqual(r_data["destination_path"], dest_path)
        self.assertEqual(r_data["recursive"], True)

    def test_transfer_add_symlink_item(self):
        """
        Adds a transfer_symlink_item to TransferData, verifies results
        """
        # add item
        source_path = "source/path/"
        dest_path = "dest/path/"
        self.tdata.add_symlink_item(source_path, dest_path)
        # verify results
        self.assertEqual(len(self.tdata["DATA"]), 1)
        data = self.tdata["DATA"][0]
        self.assertEqual(data["DATA_TYPE"], "transfer_symlink_item")
        self.assertEqual(data["source_path"], source_path)
        self.assertEqual(data["destination_path"], dest_path)

    def test_delete_init(self):
        """
        Verifies DeleteData field initialization
        """

        # default init
        default_ddata = globus_sdk.DeleteData(self.tc, GO_EP1_ID)
        self.assertEqual(default_ddata["DATA_TYPE"], "delete")
        self.assertEqual(default_ddata["endpoint"], GO_EP1_ID)
        self.assertIn("submission_id", default_ddata)
        self.assertIn("DATA", default_ddata)
        self.assertEqual(len(default_ddata["DATA"]), 0)

        # init with params
        label = "label"
        params = {"param1": "value1", "param2": "value2"}
        param_ddata = globus_sdk.DeleteData(self.tc, GO_EP1_ID,
                                            label=label,
                                            recursive="True",
                                            **params)
        self.assertEqual(param_ddata["label"], label)
        self.assertEqual(param_ddata["recursive"], "True")
        for par in params:
            self.assertEqual(param_ddata[par], params[par])

    def test_delete_add_item(self):
        """
        Adds an item to DeleteData, verifies results
        """
        # add item
        path = "source/path/"
        self.ddata.add_item(path)
        # verify results
        self.assertEqual(len(self.ddata["DATA"]), 1)
        data = self.ddata["DATA"][0]
        self.assertEqual(data["DATA_TYPE"], "delete_item")
        self.assertEqual(data["path"], path)

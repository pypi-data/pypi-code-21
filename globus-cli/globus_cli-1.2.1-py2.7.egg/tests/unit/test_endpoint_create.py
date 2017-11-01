import json
import re

from tests.framework.cli_testcase import CliTestCase
from tests.framework.constants import GO_EP1_ID


class EndpointCreateTests(CliTestCase):

    def setUp(self):
        """
        Creates a list for tracking assets for cleanup
        """
        super(EndpointCreateTests, self).setUp()

        # track list of all endpoints created during testing
        self.asset_cleanup = []

    def tearDown(self):
        """
        Deletes all endpoints created during testing
        """
        super(EndpointCreateTests, self).tearDown()
        for endpoint_id in self.asset_cleanup:
            self.tc.delete_endpoint(endpoint_id)

    def test_gcp_creation(self):
        """
        Runs endpoint create with --personal
        Confirms personal endpoint is created successfully
        """
        output = self.run_line(
            "globus endpoint create --personal personal_create -F json")
        res = json.loads(output)
        self.assertEqual(res["DATA_TYPE"], "endpoint_create_result")
        self.assertEqual(res["code"], "Created")
        self.assertIn("id", res)
        # track asset for cleanup
        self.asset_cleanup.append(res["id"])

    def test_shared_creation(self):
        """
        Runs endpoint create with --shared and a host path
        Confirms shared endpoint is created successfully
        """
        output = self.run_line("globus endpoint create share_create "
                               "-F json --shared {}:/~/".format(GO_EP1_ID))
        res = json.loads(output)
        self.assertEqual(res["DATA_TYPE"], "endpoint_create_result")
        self.assertEqual(res["code"], "Created")
        self.assertIn("Shared endpoint", res["message"])
        self.assertIn("id", res)
        # track asset for cleanup
        self.asset_cleanup.append(res["id"])

    def test_gcs_creation(self):
        """
        Runs endpoint create with --server
        Confirms endpoint is created successfully
        """
        output = self.run_line("globus endpoint create gcs_create "
                               "--server -F json")
        res = json.loads(output)
        self.assertEqual(res["DATA_TYPE"], "endpoint_create_result")
        self.assertEqual(res["code"], "Created")
        self.assertIsNone(res["globus_connect_setup_key"])
        self.assertIn("id", res)
        # track asset for cleanup
        self.asset_cleanup.append(res["id"])

    def test_text_ouptut(self):
        """
        Creates GCP and GCS endpoint
        Confirms (non)presence of setup key in text output
        """
        # GCP
        output = self.run_line(
            "globus endpoint create gcp_text --personal")
        self.assertIn("Setup Key:", output)
        ep_id = re.search("Endpoint ID:\s*(\S*)", output).group(1)
        self.asset_cleanup.append(ep_id)

        # GCS
        output = self.run_line(
            "globus endpoint create gcs_text --server")
        self.assertNotIn("Setup Key:", output)
        ep_id = re.search("Endpoint ID:\s*(\S*)", output).group(1)
        self.asset_cleanup.append(ep_id)

    def test_general_options(self):
        """
        Creates a shared, personal, and server endpoints using options
        available for all endpoint types. Confirms expected values through SDK
        """
        # options with the same option value and expected value
        same_value_dict = [
            {"opt": "--description", "key": "description", "val": "sometext"},
            {"opt": "--default-directory", "key": "default_directory",
             "val": "/share/"},
            {"opt": "--organization", "key": "organization", "val": "someorg"},
            {"opt": "--department", "key": "department", "val": "somedept"},
            {"opt": "--keywords", "key": "keywords", "val": "some,key,words"},
            {"opt": "--contact-email", "key": "contact_email", "val": "a@b.c"},
            {"opt": "--contact-info", "key": "contact_info", "val": "info"},
            {"opt": "--info-link", "key": "info_link", "val": "http://a.b"},
        ]
        # options that have differing option values and expected values
        diff_value_dict = [
            {"opt": "--force-encryption", "key": "force_encryption",
             "val": "", "expected": True},
            {"opt": "--disable-verify", "key": "disable_verify",
             "val": "", "expected": True}
        ]

        # for each endpoint type
        for ep_type in ["--shared {}:/~/".format(GO_EP1_ID),
                        "--personal",
                        "--server"]:

            # make and run the line, get and track the id for cleanup
            line = ("globus endpoint create general_options "
                    "-F json {} ".format(ep_type))
            for item in same_value_dict + diff_value_dict:
                line += "{} {} ".format(item["opt"], item["val"])
            ep_id = json.loads(self.run_line(line))["id"]
            self.asset_cleanup.append(ep_id)

            # get and confirm values from SDK get_endpoint
            res = self.tc.get_endpoint(ep_id)
            for item in same_value_dict:
                self.assertEqual(item["val"], res[item["key"]])
            for item in diff_value_dict:
                self.assertEqual(item["expected"], res[item["key"]])

    def test_server_only_options(self):
        """
        Runs endpoint create with options only valid for GCS
        Confirms expected values gotten through SDK
        """
        # options with the same option value and expected value
        same_value_dict = [
            {"opt": "--myproxy-dn", "key": "myproxy_dn", "val": "/dn"},
            {"opt": "--myproxy-server", "key": "myproxy_server", "val": "srv"},
        ]
        # options that have differing option values and expected values
        diff_value_dict = [
            {"opt": "--private", "key": "public",
             "val": "", "expected": False},
            {"opt": "--location", "key": "location",
             "val": "1.1,2", "expected": "1.10,2.00"},
        ]

        # make and run the line, get and track the id for cleanup
        line = ("globus endpoint create valid_gcs "
                "--server -F json ")
        for item in same_value_dict + diff_value_dict:
            line += "{} {} ".format(item["opt"], item["val"])
        ep_id = json.loads(self.run_line(line))["id"]
        self.asset_cleanup.append(ep_id)

        # get and confirm values from SDK get_endpoint
        res = self.tc.get_endpoint(ep_id)
        for item in same_value_dict:
            self.assertEqual(item["val"], res[item["key"]])
        for item in diff_value_dict:
            self.assertEqual(item["expected"], res[item["key"]])

    # TODO: test against a managed endpoint
    # def test_valid_managed_options(self):

    def test_invalid_gcs_only_options(self):
        """
        For all GCS only options, tries to create a GCP and shared endpoint
        Confirms invalid options are caught at the CLI level rather than API
        """
        options = ["--public", "--private", "--myproxy-dn /dn",
                   "--myproxy-server mpsrv", "--oauth-server oasrv",
                   "--location 1,1"]
        for opt in options:
            for ep_type in ["--shared {}:/~/".format(GO_EP1_ID),
                            "--personal"]:
                output = self.run_line(("globus endpoint create invalid_gcs "
                                        "{} {} ".format(ep_type, opt)),
                                       assert_exit_code=2)
                self.assertIn("Globus Connect Server", output)

    def test_invalid_managed_only_options(self):
        """
        For all managed only options, tries to create a GCS endpoint
        Confirms invalid options are caught at the CLI level rather than AP
        """
        options = ["--network-use custom", "--max-concurrency 2",
                   "--preferred-concurrency 1", "--max-parallelism 2",
                   "--preferred-parallelism 1"]
        for opt in options:
            output = self.run_line(("globus endpoint create invalid_managed "
                                    "--server {}".format(opt)),
                                   assert_exit_code=2)
            self.assertIn("managed endpoints", output)

from tests.framework.cli_testcase import CliTestCase
from tests.framework.constants import GO_EP1_ID


class EndpointCreateTests(CliTestCase):

    def setUp(self):
        """
        Creates shared, GCP, and GCS endpoints for testing
        """
        super(EndpointCreateTests, self).setUp()

        shared_data = {"DATA_TYPE": "shared_endpoint",
                       "host_endpoint": GO_EP1_ID,
                       "host_path": "/~/",
                       "display_name": "shared_update"}
        self.shared_ep = self.tc.create_shared_endpoint(shared_data)["id"]

        server_data = {"display_name": "server_update"}
        self.server_ep = self.tc.create_endpoint(server_data)["id"]

        personal_data = {"display_name": "personal_update",
                         "is_globus_connect": True}
        self.personal_ep = self.tc.create_endpoint(personal_data)["id"]

    def tearDown(self):
        """
        Deletes the endpoints created for testing
        """
        super(EndpointCreateTests, self).tearDown()
        for ep_id in [self.shared_ep, self.personal_ep, self.server_ep]:
            self.tc.delete_endpoint(ep_id)

    def test_general_options(self):
        """
        Runs endpoint update with parameters allowed for all endpoint types
        Confirms all endpoint types are successfully updated
        """
        # options with the same option value and expected value
        same_value_dict = [
            {"opt": "--display-name", "key": "display_name", "val": "newname"},
            {"opt": "--description", "key": "description", "val": "newtext"},
            {"opt": "--default-directory", "key": "default_directory",
             "val": "/share/"},
            {"opt": "--organization", "key": "organization", "val": "neworg"},
            {"opt": "--department", "key": "department", "val": "newdept"},
            {"opt": "--keywords", "key": "keywords", "val": "new,key,words"},
            {"opt": "--contact-email", "key": "contact_email", "val": "a@b.c"},
            {"opt": "--contact-info", "key": "contact_info", "val": "newinfo"},
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
        for ep_id in [self.shared_ep, self.personal_ep, self.server_ep]:

            # make and run the line
            line = ("globus endpoint update {} -F json ".format(ep_id))
            for item in same_value_dict + diff_value_dict:
                line += "{} {} ".format(item["opt"], item["val"])
            self.run_line(line)

            # get and confirm values from SDK get_endpoint
            res = self.tc.get_endpoint(ep_id)
            for item in same_value_dict:
                self.assertEqual(item["val"], res[item["key"]])
            for item in diff_value_dict:
                self.assertEqual(item["expected"], res[item["key"]])

    def test_server_only_options(self):
        """
        Runs endpoint update with options only valid for GCS
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
        line = ("globus endpoint update {} -F json ".format(self.server_ep))
        for item in same_value_dict + diff_value_dict:
            line += "{} {} ".format(item["opt"], item["val"])
        self.run_line(line)

        # get and confirm values from SDK get_endpoint
        res = self.tc.get_endpoint(self.server_ep)
        for item in same_value_dict:
            self.assertEqual(item["val"], res[item["key"]])
        for item in diff_value_dict:
            self.assertEqual(item["expected"], res[item["key"]])

    # TODO: test against a managed endpoint
    # def test_managed_only_options(self):

    def test_invalid_gcs_only_options(self):
        """
        For all GCS only options, tries to update a GCP and shared endpoint
        Confirms invalid options are caught at the CLI level rather than API
        """
        options = ["--public", "--private", "--myproxy-dn /dn",
                   "--myproxy-server mpsrv", "--oauth-server oasrv",
                   "--location 1,1"]
        for opt in options:
            for ep_id in [self.shared_ep, self.personal_ep]:
                output = self.run_line(("globus endpoint update "
                                        "{} {} ".format(ep_id, opt)),
                                       assert_exit_code=2)
                self.assertIn("Globus Connect Server", output)

    def test_invalid_managed_only_options(self):
        """
        For all managed only options, tries to update a GCS endpoint
        Confirms invalid options are caught at the CLI level rather than AP
        """
        options = ["--network-use custom", "--max-concurrency 2",
                   "--preferred-concurrency 1", "--max-parallelism 2",
                   "--preferred-parallelism 1"]
        for opt in options:
            output = self.run_line(("globus endpoint update "
                                    "{} {} ".format(self.server_ep, opt)),
                                   assert_exit_code=2)
            self.assertIn("managed endpoints", output)

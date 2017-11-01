import json

from tests.framework.cli_testcase import CliTestCase
from tests.framework.tools import get_user_data


class GetIdentitiesTests(CliTestCase):
    """
    Tests get-identities command
    """

    def test_default_one_id(self):
        """
        Runs get-identities with one id, confirms correct username returned
        """
        output = self.run_line("globus get-identities " +
                               get_user_data()["clitester1a"]["id"])
        self.assertEqual(get_user_data()["clitester1a"]["username"] + "\n",
                         output)

    def test_defualt_one_username(self):
        """
        Runs get-identities with one username, confirms correct id returned
        """
        output = self.run_line("globus get-identities " +
                               get_user_data()["clitester1a"]["username"])
        self.assertEqual(get_user_data()["clitester1a"]["id"] + "\n", output)

    def test_default_invalid(self):
        """
        Runs get-identities with one username, confirms correct id returned
        """
        output = self.run_line("globus get-identities invalid")
        self.assertEqual("NO_SUCH_IDENTITY\n", output)

    def test_default_multiple_inputs(self):
        """
        Runs get-identities with id username, duplicate and invalid inputs
        Confirms order is preserved and all values are as expected
        """
        in_vals = [get_user_data()["clitester1a"]["username"],
                   get_user_data()["clitester1a"]["id"],
                   "invalid",
                   get_user_data()["go"]["username"],
                   get_user_data()["go"]["username"]]

        expected = [get_user_data()["clitester1a"]["id"],
                    get_user_data()["clitester1a"]["username"],
                    "NO_SUCH_IDENTITY",
                    get_user_data()["go"]["id"],
                    get_user_data()["go"]["id"]]

        output = self.run_line("globus get-identities " + " ".join(in_vals))
        self.assertEqual("\n".join(expected) + "\n", output)

    def test_verbose(self):
        """
        Runs get-identities with --verbose, confirms expected fields found
        """
        go_data = get_user_data()["go"]
        output = self.run_line("globus get-identities --verbose " +
                               go_data["id"])
        for key in ["username", "id", "name", "organization", "email"]:
            self.assertIn(go_data[key], output)

    def test_json(self):
        """
        Runs get-identities with -F json confirms expected values
        """
        go_data = get_user_data()["go"]
        output = json.loads(self.run_line("globus get-identities -F json " +
                                          go_data["id"]))
        for key in go_data:
            self.assertIn(go_data[key], output["identities"][0][key])

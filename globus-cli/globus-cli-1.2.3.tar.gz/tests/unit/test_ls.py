from tests.framework.cli_testcase import CliTestCase
from tests.framework.constants import GO_EP1_ID


class LsTests(CliTestCase):
    """
    Tests globus ls command
    """

    def test_path(self):
        """
        Does an ls on EP1:/, confirms expected results.
        """
        path = "/"
        output = self.run_line("globus ls {}:{}".format(GO_EP1_ID, path))

        expected = ["home/", "mnt/", "not shareable/", "share/"]
        for item in expected:
            self.assertIn(item, output)

    def test_recursive(self):
        """
        Confirms --recursive ls on EP1:/share/ finds file1.txt
        """
        output = self.run_line("globus ls -r {}:/share/".format(GO_EP1_ID))
        self.assertIn("file1.txt", output)

    def test_depth(self):
        """
        Confirms setting depth to 1 on a --recursive ls of EP1:/
        finds godata but not file1.txt
        """
        output = self.run_line(("globus ls -r --recursive-depth-limit 1 {}:/"
                                .format(GO_EP1_ID)))
        self.assertNotIn("file1.txt", output)

    def test_recursive_json(self):
        """
        Confirms -F json works with the RecursiveLsResponse
        """
        output = self.run_line(
            "globus ls -r -F json {}:/share".format(GO_EP1_ID))
        self.assertIn('"DATA":', output)
        self.assertIn('"name": "godata/file1.txt"', output)

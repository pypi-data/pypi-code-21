from tests.framework.cli_testcase import CliTestCase
from tests.framework.constants import GO_EP1_ID


class OneUseOption(CliTestCase):

    def test_multiple_argument_options(self):
        """
        Runs endpoint create with two --shared options
        Confirms exit code is 2 after click.BadParamater is raised
        """
        output = self.run_line((
            "globus endpoint create ep_name "
            "--shared {0}:/ --shared {0}:/".format(GO_EP1_ID)),
            assert_exit_code=2)

        self.assertIn('Invalid value for "--shared"', output)
        self.assertIn("Option used multiple times.", output)

    def test_multiple_flag_options(self):
        """
        Runs endpoint create with two --personal options
        Confirms exit code is 2 after click.BadParamater is raised
        """
        output = self.run_line(
            "globus endpoint create ep_name --personal --personal",
            assert_exit_code=2)

        self.assertIn('Invalid value for "--personal"', output)
        self.assertIn("Option used multiple times.", output)

import unittest
try:
    from mock import patch
except ImportError:
    from unittest.mock import patch
import six
import shlex
from click.testing import CliRunner
from datetime import datetime, timedelta
from configobj import ConfigObj

import globus_sdk

from globus_cli import main
from globus_cli.config import (
    AUTH_RT_OPTNAME, AUTH_AT_OPTNAME, AUTH_AT_EXPIRES_OPTNAME,
    TRANSFER_RT_OPTNAME, TRANSFER_AT_OPTNAME, TRANSFER_AT_EXPIRES_OPTNAME,
    WHOAMI_ID_OPTNAME, WHOAMI_USERNAME_OPTNAME, WHOAMI_NAME_OPTNAME,
    WHOAMI_EMAIL_OPTNAME)
from globus_cli.services.transfer import get_client
from globus_cli.services.auth import get_auth_client

from tests.framework.constants import (CLITESTER1A_TRANSFER_RT,
                                       CLITESTER1A_AUTH_RT, GO_EP1_ID)
from tests.framework.tools import get_user_data


def clean_sharing():
    """
    Cleans out any files in ~/.globus/sharing/ on go#ep1 older than an hour
    TODO: remove this once deleting shared directories does full cleanup
    """
    tc = get_client()

    path = "~/.globus/sharing/"
    hour_ago = datetime.utcnow() - timedelta(hours=1)
    filter_string = "last_modified:," + hour_ago.strftime("%Y-%m-%d %H:%M:%S")
    try:
        old_files = tc.operation_ls(
            GO_EP1_ID, path=path, filter=filter_string, num_results=None)
    except globus_sdk.TransferAPIError:
        return

    kwargs = {"notify_on_succeeded": False, "notify_on_fail": False}
    ddata = globus_sdk.DeleteData(tc, GO_EP1_ID, **kwargs)

    for item in old_files:
        ddata.add_item(path + item["name"])

    if len(ddata["DATA"]):
        tc.submit_delete(ddata)


def default_test_config(*args, **kwargs):
    """
    Returns a ConfigObj with the clitester's refresh tokens and whoami info
    as if the clitester was logged in and a call to get_config_obj was made.
    """
    user_data = get_user_data()["clitester1a"]

    # create a ConfgObj from a dict of testing constants. a ConfigObj created
    # this way will not be tied to a config file on disk, meaning that
    # ConfigObj.filename = None and ConfigObj.write() returns a string without
    # writing anything to disk.
    return ConfigObj({"cli": {
        AUTH_RT_OPTNAME: CLITESTER1A_AUTH_RT,
        AUTH_AT_OPTNAME: "",
        AUTH_AT_EXPIRES_OPTNAME: 0,
        TRANSFER_RT_OPTNAME: CLITESTER1A_TRANSFER_RT,
        TRANSFER_AT_OPTNAME: "",
        TRANSFER_AT_EXPIRES_OPTNAME: 0,
        WHOAMI_ID_OPTNAME: user_data["id"],
        WHOAMI_USERNAME_OPTNAME: user_data["username"],
        WHOAMI_NAME_OPTNAME: user_data["name"],
        WHOAMI_EMAIL_OPTNAME: user_data["email"]
        }
    })


class CliTestCase(unittest.TestCase):
    """
    A class of TestCases which test the CLI by making direct calls to the CLI
    and then testing the results. Uses testing refresh tokens to authorize
    calls, and wraps a click CliRunner for running commands.
    """
    def __init__(self, desc):
        unittest.TestCase.__init__(self, desc)
        self._runner = CliRunner()

    @classmethod
    @patch("globus_cli.config.get_config_obj", new=default_test_config)
    def setUpClass(self):
        """
        Gets a TransferClient and AuthClient for direct sdk calls
        Cleans any old sharing data created by previous test runs
        """
        self.tc = get_client()
        self.ac = get_auth_client()
        clean_sharing()

    @patch("globus_cli.config.get_config_obj")
    def run_line(self, line, mock_config, config=None,
                 assert_exit_code=0, batch_input=None):
        """
        Uses the CliRunner to run the given command line.

        Any calls to get_config_obj during the test are patched to
        return a ConfigObj with given config dict. If no config dict is given,
        defaults to default_test_config_obj defined above.

        Asserts that the exit_code is equal to the given assert_exit_code,
        and if that exit_code is 0 prevents click from catching exceptions
        for easier debugging.

        Any given batch_input is passed as input to stdin.
        """
        # mock out calls to get_config_obj to return given config
        # if none given default to default test config values
        if config is None:
            mock_config.return_value = default_test_config()
        else:
            mock_config.return_value = ConfigObj(config)

        # split line into args and confirm line starts with "globus"
        # python2 shlex can't handle non ascii unicode
        if six.PY2 and isinstance(line, six.text_type):
            args = [a for a in shlex.split(line.encode("utf-8"))]
        else:
            args = shlex.split(line)
        self.assertEqual(args[0], "globus")

        # run the line. globus_cli.main is the "globus" part of the line
        # if we are expecting success (0), don't catch any exceptions.
        result = self._runner.invoke(main, args[1:], input=batch_input,
                                     catch_exceptions=bool(assert_exit_code))
        # confirm expected exit_code
        if result.exit_code != assert_exit_code:
            if isinstance(line, six.binary_type):
                line = line.decode("utf-8")
            raise(Exception(
                (u"CliTest run_line exit_code assertion failed!\n"
                 "Line: {}\nexited with {} when expecting {}\n"
                 "Output: {}".format(line, result.exit_code,
                                     assert_exit_code, result.output))))
        # return the output for further testing
        return result.output

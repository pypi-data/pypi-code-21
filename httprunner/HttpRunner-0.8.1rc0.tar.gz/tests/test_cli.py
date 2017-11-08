import sys

from httprunner import exception, cli
from tests.base import ApiServerUnittest


class TestCli(ApiServerUnittest):

    def test_ate(self):

        cli.main_ate()

        print(sys.stdout)

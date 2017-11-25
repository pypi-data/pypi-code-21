from shuup_testutils.cases.snake import SnakeTestCase
from shuup_testutils.cases.clients import AuthAdminClient
from shuup_testutils.cases.clients import AuthUserClient
from shuup_testutils.cases.clients import ApiAuthAdminClient


# TODO rename into ApiAdminTestCase
class ApiAuthAdminTestCase(SnakeTestCase):
    client_class = ApiAuthAdminClient

    @classmethod
    def set_up_class(cls):
        cls.init_shuup()

    def set_up(self):
        self.client.init()


# TODO rename into AdminTestCase
class AuthAdminTestCase(SnakeTestCase):
    client_class = AuthAdminClient

    @classmethod
    def set_up_class(cls):
        cls.init_shuup()

    def set_up(self):
        self.client.init()


# TODO rename into AdminTestCase
class AuthUserTestCase(SnakeTestCase):
    client_class = AuthUserClient

    @classmethod
    def set_up_class(cls):
        cls.init_shuup()

    def set_up(self):
        self.client.init()

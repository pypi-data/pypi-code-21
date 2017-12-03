import trust
import json
from trust.exceptions import AuthenticationException, FormatterException
from .logged_tests import LoggedTests


class TestTrust(LoggedTests):
    def test_response_mode_json(self):
        actual = self._process_list_using_response_type("json")
        expected = '{"result": [3, 7, 1]}'
        self.assertEqual(expected, actual)

    def test_response_mode_complete(self):
        actual = self._process_list_using_response_type("complete")
        expected = "[3, 7, 1]"
        self.assertEqual(expected, actual)

    def test_response_mode_text(self):
        actual = self._process_list_using_response_type("text")
        expected = "3\n7\n1"
        self.assertEqual(expected, actual)

    def test_response_mode_empty(self):
        actual = self._process_list_using_response_type("")
        expected = "[3, 7, 1]"
        self.assertEqual(expected, actual)

    def test_response_mode_other(self):
        with self.assertRaises(FormatterException) as context:
            actual = self._process_list_using_response_type("something else")

    def test_no_credentials(self):
        class FinderMock():
            def __init__(self):
                self.find_called = False

            def access_as(self, credentials):
                pass

            def find(self, query, optional):
                self.find_called = True

        mock = FinderMock()
        result = trust.Trust(mock).process(
            "/", "complete", trust.Credentials.get_empty()
        )

        self.assertTrue(mock.find_called)

    def _process_list_using_response_type(self, response_type):
        class FinderStub():
            def access_as(self, credentials):
                pass

            def find(self, query, optional):
                return [3, 7, 1]

        return trust.Trust(FinderStub()).process(
            "/", response_type, trust.Credentials.get_empty()
        )


class FinderStubAlwaysFailAuthentication():
    def access_as(self, credentials):
        pass

    def find(self, query, optional):
        raise AuthenticationException

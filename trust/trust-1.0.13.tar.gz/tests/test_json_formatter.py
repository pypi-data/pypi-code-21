import json
import trust
import trust.formatters
from trust.exceptions import AuthenticationException
from .formatter_tests import FormatterTests, FinderStubWithValue


class TestJsonFormatter(FormatterTests):
    def test_none(self):
        actual = self._process_default(None)
        expected = '{"result": null}'
        self.assertEqual(expected, actual)

    def test_int(self):
        actual = self._process_default(5)
        expected = '{"result": 5}'
        self.assertEqual(expected, actual)

    def test_float(self):
        actual = self._process_default(5.0)
        expected = '{"result": 5.0}'
        self.assertEqual(expected, actual)

    def test_string(self):
        actual = self._process_default("Hello")
        expected = '{"result": "Hello"}'
        self.assertEqual(expected, actual)

    def test_object(self):
        actual = self._process_default({"Hello": 2})
        expected = '{"result": {"Hello": 2}}'
        self.assertEqual(expected, actual)

    def test_list(self):
        actual = self._process_default([3, 7, 1])
        expected = '{"result": [3, 7, 1]}'
        self.assertEqual(expected, actual)

    def test_list_of_objects(self):
        actual = self._process_default([3, "abc", {"hello": "world"}])
        expected = '{"result": [3, "abc", {"hello": "world"}]}'
        self.assertEqual(expected, actual)

    def test_wrong_credentials(self):
        class FinderStub():
            def access_as(self, credentials):
                pass

            def find(self, query, optional):
                raise AuthenticationException()

        result = self._get_formatter(FinderStub()).process(
            "/", trust.Credentials("Lucy", "demo")
        )

        self._logger.debug("Got response %s.", result)
        actual = json.loads(result)["errors"][0]["type"]
        expected = "credentials-invalid"
        self.assertEqual(expected, actual)

    def test_no_enough_permissions(self):
        class FinderStub():
            def access_as(self, credentials):
                pass

            def find(self, query, optional):
                raise PermissionError()

        result = self._get_formatter(FinderStub()).process(
            "/", trust.Credentials("Lucy", "demo")
        )

        self._logger.debug("Got response %s.", result)
        actual = json.loads(result)["errors"][0]["type"]
        expected = "permission-required"
        self.assertEqual(expected, actual)

    def _get_formatter(self, finder):
        return trust.formatters.JsonFormatter(finder)

import trust
import trust.formatters
from trust.exceptions import AuthenticationException
from .formatter_tests import FormatterTests, FinderStubWithValue


class TestTextFormatter(FormatterTests):
    def test_none(self):
        actual = self._process_default(None)
        expected = ""
        self.assertEqual(expected, actual)

    def test_int(self):
        actual = self._process_default(5)
        expected = "5"
        self.assertEqual(expected, actual)

    def test_float(self):
        actual = self._process_default(5.0)
        expected = "5.0"
        self.assertEqual(expected, actual)

    def test_string(self):
        actual = self._process_default("Hello")
        expected = "Hello"
        self.assertEqual(expected, actual)

    def test_object(self):
        actual = self._process_default({"Hello": 2})
        expected = '{"Hello": 2}'
        self.assertEqual(expected, actual)

    def test_list(self):
        actual = self._process_default([3, 7, 1])
        expected = "3\n7\n1"
        self.assertEqual(expected, actual)

    def test_list_of_objects(self):
        actual = self._process_default([3, "abc", {"hello": "world"}])
        expected = '3\nabc\n{"hello": "world"}'
        self.assertEqual(expected, actual)

    def test_wrong_credentials(self):
        class FinderStub():
            def access_as(self, credentials):
                pass

            def find(self, query, optional):
                raise AuthenticationException

        with self.assertRaises(AuthenticationException) as context:
            self._get_formatter(FinderStub()).process(
                "/", trust.Credentials("Lucy", "demo")
            )

    def _get_formatter(self, finder):
        return trust.formatters.TextFormatter(finder)

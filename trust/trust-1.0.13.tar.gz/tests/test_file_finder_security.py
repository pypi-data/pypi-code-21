import trust
import trust.exceptions
from .common_tests import CommonTests


class TestFileFinderSecurity(CommonTests):
    def test_guest(self):
        self._writeJson(
            "hello.json", {
                ".special:restricted": {}
            }
        )

        with self.assertRaises(PermissionError) as context:
            self._finder.find("/hello")

    def test_guest_child(self):
        self._writeJson(
            "hello.json", {
                ".special:restricted": {},
                "world": "Hello"
            }
        )

        with self.assertRaises(PermissionError) as context:
            self._finder.find("/hello/world")

    def test_guest_parent(self):
        self._writeJson(
            "hello.json", {
                "hello": "Hello, World!",
                "world": {
                    ".special:restricted": {},
                }
            }
        )

        actual = self._finder.find("/hello")
        expected = {
            "hello": "Hello, World!",
            "world": None
        }

        self.assertEqual(expected, actual)

    def test_guest_inheritance(self):
        self._writeJson(
            "parent.json", {
                ".special:restricted": {}
            }
        )

        self._writeJson(
            "child.json", {
                ".special:inherit": "/parent",
                "hello": 2
            }
        )

        with self.assertRaises(PermissionError) as context:
            self._finder.find("/child/world")

    def test_user_getter_default(self):
        actual = self._finder.username
        self.assertIsNone(actual)

    def test_user_getter(self):
        class AuthStub():
            def verify(self, credentials):
                return True

        finder = self._finder
        finder.auth_provider = AuthStub()
        finder.access_as(trust.Credentials("John", "demo"))
        actual = finder.username
        expected = "John"
        self.assertEqual(expected, actual)

    def test_authentication_invalid(self):
        class AuthStub():
            def verify(self, credentials):
                return False

        self._writeJson(
            "hello.json", {
                ".special:restricted": {
                    "users": ["John"]
                },
                "world": "Hello"
            }
        )

        finder = self._finder
        finder.auth_provider = AuthStub()
        finder.access_as(trust.Credentials("John", "demo"))
        with self.assertRaises(
                trust.exceptions.AuthenticationException) as context:
            finder.find("/hello")

    def test_user(self):
        class AuthStub():
            def verify(self, credentials):
                return True

        self._writeJson(
            "hello.json", {
                ".special:restricted": {
                    "users": ["John"]
                },
                "world": "Hello"
            }
        )

        finder = self._finder
        finder.auth_provider = AuthStub()
        finder.access_as(trust.Credentials("John", "demo"))
        actual = finder.find("/hello")
        expected = {
            "world": "Hello"
        }

        self.assertEqual(expected, actual)

    def test_user_child(self):
        class AuthStub():
            def verify(self, credentials):
                return True

        self._writeJson(
            "hello.json", {
                ".special:restricted": {
                    "users": ["John"]
                },
                "world": "Hello"
            }
        )

        finder = self._finder
        finder.auth_provider = AuthStub()
        finder.access_as(trust.Credentials("John", "demo"))
        actual = finder.find("/hello/world")
        expected = "Hello"
        self.assertEqual(expected, actual)

    def test_user_parent(self):
        class AuthStub():
            def verify(self, credentials):
                return True

        self._writeJson(
            "hello.json", {
                "child": {
                    ".special:restricted": {
                        "users": ["John"]
                    },
                    "world": "Hello"
                }
            }
        )

        finder = self._finder
        finder.auth_provider = AuthStub()
        finder.access_as(trust.Credentials("John", "demo"))
        actual = finder.find("/hello")
        expected = {
            "child": {
                "world": "Hello"
            }
        }

        self.assertEqual(expected, actual)

    def test_user_outside_list(self):
        class AuthStub():
            def verify(self, credentials):
                return True

        self._writeJson(
            "hello.json", {
                ".special:restricted": {
                    "users": ["Lucy"]
                },
                "world": "Hello"
            }
        )

        finder = self._finder
        finder.auth_provider = AuthStub()
        finder.access_as(trust.Credentials("John", "demo"))
        with self.assertRaises(PermissionError) as context:
            actual = finder.find("/hello/world")

    def test_group(self):
        class AuthStub():
            def verify(self, credentials):
                return True

            def ingroup(self, username, groupname):
                return True

        self._writeJson(
            "hello.json", {
                ".special:restricted": {
                    "users": ["Lucy"],
                    "groups": ["Backup operators"]
                },
                "world": "Hello"
            }
        )

        finder = self._finder
        finder.auth_provider = AuthStub()
        finder.access_as(trust.Credentials("John", "demo"))
        actual = finder.find("/hello/world")
        expected = "Hello"
        self.assertEqual(expected, actual)

    def test_not_in_group(self):
        class AuthStub():
            def verify(self, credentials):
                return True

            def ingroup(self, username, groupname):
                return False

        self._writeJson(
            "hello.json", {
                ".special:restricted": {
                    "users": ["Lucy"],
                    "groups": ["Backup operators"]
                },
                "world": "Hello"
            }
        )

        finder = self._finder
        finder.auth_provider = AuthStub()
        finder.access_as(trust.Credentials("John", "demo"))
        with self.assertRaises(PermissionError) as context:
            finder.find("/hello/world")

    def test_special_value(self):
        class AuthStub():
            def verify(self, credentials):
                return True

        self._writeJson(
            "hello.json", {
                ".special:restricted": {
                    "users": ["John"]
                },
                ".special:value": "Hello"
            }
        )

        finder = self._finder
        finder.auth_provider = AuthStub()
        finder.access_as(trust.Credentials("John", "demo"))
        actual = finder.find("/hello")
        expected = "Hello"

        self.assertEqual(expected, actual)

    def test_special_value_object(self):
        class AuthStub():
            def verify(self, credentials):
                return True

        self._writeJson(
            "hello.json", {
                ".special:restricted": {
                    "users": ["John"]
                },
                ".special:value": {
                    "world": "Hello"
                }
            }
        )

        finder = self._finder
        finder.auth_provider = AuthStub()
        finder.access_as(trust.Credentials("John", "demo"))
        actual = finder.find("/hello/world")
        expected = "Hello"

        self.assertEqual(expected, actual)

    def test_no_auth_if_public(self):
        class AuthMock():
            def __init__(self):
                self.verify_called = False

            def verify(self, credentials):
                self.verify_called = True
                return True

        self._writeJson(
            "hello.json", {
                "world": "Hello, World"
            }
        )

        mock = AuthMock()
        finder = self._finder
        finder.auth_provider = mock
        finder.access_as(trust.Credentials("John", "demo"))
        actual = finder.find("/hello/world")

        self.assertFalse(mock.verify_called)

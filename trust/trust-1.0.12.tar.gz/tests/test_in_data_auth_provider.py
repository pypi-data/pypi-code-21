import trust
import trust.auth
from .common_tests import CommonTests


class TestInDataAuthProvider(CommonTests):
    def test_verify_right(self):
        self._writeJson(
            "_users.json", {
                "sample": {
                    "hash": ("$pbkdf2-sha256$10$1hpjzFnLubf2/j9nrPVeaw$DJBUI" +
                             "hmaa2U8.11dfh5cueJBAEfK0MWflMNL7oCJXpY")
                }
            })

        result = self._auth.verify(
            trust.Credentials("sample", "correct password")
        )

        self.assertTrue(result)

    def test_verify_wrong(self):
        self._writeJson(
            "_users.json", {
                "sample": {
                    "hash": ("$pbkdf2-sha256$10$1hpjzFnLubf2/j9nrPVeaw$DJBUI" +
                             "hmaa2U8.11dfh5cueJBAEfK0MWflMNL7oCJXpY")
                }
            })

        result = self._auth.verify(
            trust.Credentials("sample", "I'm the wrong password")
        )

        self.assertFalse(result)

    def test_ingroup_right(self):
        self._writeJson(
            "_users.json", {
                "sample": {
                    "member-of": ["a"]
                }
            })

        self._writeJson(
            "_groups.json", {
                "a": {}
            }
        )

        result = self._auth.ingroup("sample", "a")
        self.assertTrue(result)

    def test_ingroup_wrong(self):
        self._writeJson(
            "_users.json", {
                "sample": {
                    "member-of": ["a"]
                }
            })

        self._writeJson(
            "_groups.json", {
                "a": {}
            }
        )

        result = self._auth.ingroup("sample", "b")
        self.assertFalse(result)

    def test_ingroup_tree(self):
        self._writeJson(
            "_users.json", {
                "sample": {
                    "member-of": ["a"]
                }
            })

        self._writeJson(
            "_groups.json", {
                "a": {
                    "member-of": ["b"]
                }
            }
        )

        result = self._auth.ingroup("sample", "b")
        self.assertTrue(result)

    def test_ingroup_circular(self):
        self._writeJson(
            "_users.json", {
                "sample": {
                    "member-of": ["a"]
                }
            })

        self._writeJson(
            "_groups.json", {
                "a": {
                    "member-of": ["b"]
                },
                "b": {
                    "member-of": ["a"]
                }
            }
        )

        result = self._auth.ingroup("sample", "c")
        self.assertFalse(result)

    def test_ingroup_self_referencing(self):
        self._writeJson(
            "_users.json", {
                "sample": {
                    "member-of": ["a"]
                }
            })

        self._writeJson(
            "_groups.json", {
                "a": {
                    "member-of": ["a"]
                }
            }
        )

        result = self._auth.ingroup("sample", "b")
        self.assertFalse(result)

    @property
    def _auth(self):
        return trust.auth.InDataAuthProvider(self._finder, self._logger)

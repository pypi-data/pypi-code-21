import unittest


class TestZpasswdDeprecation(unittest.TestCase):

    def test(self):
        from zope.app.server.zpasswd import Principal  # noqa

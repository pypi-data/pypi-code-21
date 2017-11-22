#-*- coding: utf-8 -*-
"""
@brief      test log(time=1s)
"""

import sys
import os
import unittest
import tornado


try:
    import pyquickhelper as skip_
except ImportError:
    path = os.path.normpath(
        os.path.abspath(
            os.path.join(
                os.path.split(__file__)[0],
                "..",
                "..",
                "..",
                "pyquickhelper",
                "src")))
    if path not in sys.path:
        sys.path.append(path)
    import pyquickhelper as skip_


try:
    import src
except ImportError:
    path = os.path.normpath(
        os.path.abspath(
            os.path.join(
                os.path.split(__file__)[0],
                "..",
                "..")))
    if path not in sys.path:
        sys.path.append(path)
    import src

from tornado.testing import AsyncTestCase
from tornado.httpclient import AsyncHTTPClient


class TestHttp(AsyncTestCase):

    @tornado.testing.gen_test
    def test_http_fetch(self):
        client = AsyncHTTPClient(self.io_loop)
        response = yield client.fetch("http://www.xavierdupre.fr")
        self.assertIn(b"Xavier", response.body)


if __name__ == "__main__":
    unittest.main()

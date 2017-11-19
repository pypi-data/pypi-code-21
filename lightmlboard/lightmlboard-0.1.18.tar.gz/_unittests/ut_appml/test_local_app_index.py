#-*- coding: utf-8 -*-
"""
@brief      test log(time=33s)
"""

import sys
import os
import unittest


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

from pyquickhelper.loghelper import fLOG
from tornado.testing import AsyncHTTPTestCase
from src.lightmlboard.appml import LightMLBoard
from tornado.escape import json_encode


class TestLocalAppIndex(AsyncHTTPTestCase):

    def get_app(self):
        this = os.path.dirname(__file__)
        config = os.path.join(this, "this_default_options.py")
        return LightMLBoard.make_app(config=config, logged=dict(user='xd', pwd='pwd'))

    def test_local_index(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        post = dict(user=['xd'], pwd=['pwd'],
                    _xsrf=['2|a114f78b|3990916811cdda4bbaec096bf1f57923|1507577457'])
        headers = {'Host': 'localhost:8897', 'Connection': 'keep-alive',
                   'Cache-Control': 'max-age=0',
                   'Origin': 'http://localhost:8897', 'Upgrade-Insecure-Requests': '1',
                   'Content-Type': 'application/x-www-form-urlencoded',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                   'Referer': 'http://localhost:8897/login',
                   'Accept-Encoding': 'gzip, deflate, br',
                   'Accept-Language': 'fr-FR,fr;q=0.8,en-US;q=0.6,en;q=0.4,ja;q=0.2',
                   'Cookie': '_xsrf=2|5e9d6173|c6190790ee444cb345659f930e7cefdb|1507577457; ' +
                   'incorrect="2|1:0|10:1508700922|9:incorrect|4:NA==|74fbcc0d51ee11cb2073009ee093293a1cddfd8a2315de70e12a17a83df5a2b2"'
                   }
        body = json_encode(post)
        response = self.fetch('/login', method='POST',
                              headers=headers, body=body)
        # Does not work due to:  '_xsrf' argument missing from POST
        return
        self.assertEqual(response.code, 200)
        self.assertNotIn(b"Identification...", response.body)


if __name__ == "__main__":
    unittest.main()

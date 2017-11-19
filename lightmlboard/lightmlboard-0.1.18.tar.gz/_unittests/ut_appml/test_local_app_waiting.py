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
from pyquickhelper.pycode import get_temp_folder
from tornado.testing import AsyncHTTPTestCase
from src.lightmlboard.appml import LightMLBoard
from src.lightmlboard.static import copy_static


class TestLocalAppWaiting(AsyncHTTPTestCase):

    def get_app(self):
        this = os.path.dirname(__file__)
        config = os.path.join(this, "this_default_options.py")
        return LightMLBoard.make_app(config=config, logged=dict(user='xd', pwd='pwd'))

    def test_local_waiting(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")
        response = self.fetch('/upload')
        self.assertEqual(response.code, 200)
        self.assertIn(b"<h2>Uploading</h2>", response.body)
        self.assertIn(b".gif", response.body)
        temp = get_temp_folder(__file__, "temp_local_waiting")
        page = os.path.join(temp, "waiting.html")
        with open(page, "wb") as f:
            f.write(response.body)
        copy_static(temp)


if __name__ == "__main__":
    unittest.main()

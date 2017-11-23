#-*- coding: utf-8 -*-
"""
@brief      test log(time=1s)
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
from pyquickhelper.pycode import ExtTestCase
from src.lightmlboard.competition import Competition
from src.lightmlboard.default_options import LightMLBoardDefaultOptions


class TestCompetition(ExtTestCase):

    def test_competition(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        vals = LightMLBoardDefaultOptions.competitions
        ds = [v.to_dict() for v in vals]
        vals2 = [Competition(**d) for d in ds]
        ds2 = [v.to_dict() for v in vals2]
        self.assertEqual(ds, ds2)


if __name__ == "__main__":
    unittest.main()

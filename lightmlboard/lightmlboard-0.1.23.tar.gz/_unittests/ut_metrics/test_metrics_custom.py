#-*- coding: utf-8 -*-
"""
@brief      test log(time=1s)
"""

import sys
import os
import unittest
import numpy


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
from src.lightmlboard.metrics import l1_reg_max, multi_label_jaccard


class TestMetricsCustom(ExtTestCase):

    def test_l1_reg_max(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        exp = [50, 60, 100, 180, 200]
        val = [50, 60, 100, 180, 180]
        r = l1_reg_max(exp, val)
        self.assertEqual(r, 0)

        exp = [50, 60, 100, 180, 200]
        val = [50, 60, 100, 160, 180]
        r = l1_reg_max(exp, val)
        self.assertEqual(r, 0.02222222222222222)

        exp = numpy.array(exp)
        val = numpy.array(val)

        r = l1_reg_max(exp, val)
        self.assertEqual(r, 0.02222222222222222)

        exp = {i: exp[i] for i in range(0, len(exp))}
        val = {i: val[i] for i in range(0, len(val))}
        r = l1_reg_max(exp, val)
        self.assertEqual(r, 0.02222222222222222)

        exp = [50, 60, 100, 180, 200]
        val = [50, 60, 100, 160]
        self.assertRaise(lambda: l1_reg_max(exp, val), ValueError)
        exp = numpy.array(exp)
        val = numpy.array(val)
        self.assertRaise(lambda: l1_reg_max(exp, val), ValueError)
        exp = {i: exp[i] for i in range(0, len(exp))}
        val = {i: val[i] for i in range(0, len(val))}
        self.assertRaise(lambda: l1_reg_max(exp, val), ValueError)

    def test_classification_jaccard(self):
        fLOG(
            __file__,
            self._testMethodName,
            OutputPrint=__name__ == "__main__")

        exp = ["4", "5", "6,7", [6, 7], (6, 7), {6, 7}]
        val = ["4", ["5"], "6,7", [6, 7], (6, 7), {6, 7}]
        r = multi_label_jaccard(exp, val)
        self.assertEqual(r, 1)

        exp = ["4", "5", "6,7", [6, 7], (6, 7), {6, 7}]
        val = ["4", ["5"], "7", [7], (7,), {7}]
        r = multi_label_jaccard(exp, val)
        self.assertEqual(r, 0.6666666666666666)

        val = val[:-1]
        self.assertRaise(lambda: multi_label_jaccard(exp, val), ValueError)


if __name__ == "__main__":
    unittest.main()

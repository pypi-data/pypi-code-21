# ----------------------------------------------------------------------------
# Copyright (c) 2016--, gneiss development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
# ----------------------------------------------------------------------------
import unittest
import numpy as np
from gneiss.plot import mixture_plot


class TestMixturePlot(unittest.TestCase):

    def setUp(self):
        self.spectrum = np.array(
            [0.4579667, 0.39576221, -0.39520894, -0.44957529, 0.0147894,
             0.03894491, 0.01431574, 0.02130079, 0.00530691, 0.00163606,
             0.10417575, 0.01679624, 0.01408287, 0.08377197, -0.05097175,
             0.01467061, 0.0513028, 0.03894267, 0.07682788, -0.02302689,
             0.03727277, -0.00167041, 0.06700641, 0.09992187, 0.07400123,
             -0.05075235, 0.03855951, 0.03232991, 0.033296, -0.0778636,
             -0.02262944, 0.01665713, 0.02012388, -0.08734141, 0.04402584,
             0.01885096, 0.01236461, 0.02019468, -0.01489146, -0.10339335,
             -0.0526063, -0.03070242, 0.01214559, -0.15510279, -0.04290816,
             0.04884383, 0.03615357, -0.00967101, 0.02681241, 0.01047964,
             -0.03984972, -0.0016186, 0.02497351, -0.02950191, 0.04832895,
             -0.068324, 0.00458738, 0.01106375, 0.04545569, 0.00771012,
             0.02453104, -0.01616486, 0.05563585, 0.01309359, 0.01579368,
             0.0051668, 0.01042911, -0.07541249, -0.0228381, -0.00250977,
             -0.0163356, -0.11578245, 0.00780789, -0.04505144, 0.11493317,
             0.06772574, -0.06261561, -0.08941559, -0.02147429, -0.01220844,
             -0.04686819, 0.05811476, -0.02413633, 0.14336764, -0.08111341,
             0.05834844, -0.09425382, 0.03425244, 0.05037963, -0.0336687,
             -0.06270773, 0.07621378, 0.04144562, 0.01764233, 0.05221101,
             -0.04337608, 0.06173909, -0.04485265, 0.01397837, 0.04435679,
             0.04435679, -0.01826977, -0.01877417, 0.0629691 ])

    def test_mixture_plot(self):
        a = mixture_plot(self.spectrum)
        res = a.get_lines()[0]._xy





"""
.. module:: test_viewer
   :synopsis: Unit tests for viewer module
"""

import numpy as np

from nutsflow import Consume
from nutsflow.common import Redirect
from nutsml import PrintColType

expected_col_info1 = """
item 0: <tuple>
  0: <ndarray> shape:10x20x3 dtype:float64 range:0.0..0.0
  1: <int> 1
item 1: <tuple>
  0: <str> text
  1: <int> 2
item 2: <int>
  0: <int> 3
"""

expected_col_info2 = """
item 0: <tuple>
  1: <int> 2
item 1: <tuple>
  1: <int> 4
"""

expected_col_info3 = """
item 0: <tuple>
  0: <int> 1
  1: <int> 2
item 1: <tuple>
  0: <int> 3
  1: <int> 4
"""


def test_PrintColType():
    with Redirect() as out1:
        data = [(np.zeros((10, 20, 3)), 1), ('text', 2), 3]
        data >> PrintColType() >> Consume()
    assert out1.getvalue() == expected_col_info1[1:]

    with Redirect() as out2:
        data = [(1, 2), (3, 4)]
        data >> PrintColType(1) >> Consume()
    assert out2.getvalue() == expected_col_info2[1:]

    with Redirect() as out3:
        data = [(1, 2), (3, 4)]
        data >> PrintColType((0, 1)) >> Consume()
    assert out3.getvalue() == expected_col_info3[1:]

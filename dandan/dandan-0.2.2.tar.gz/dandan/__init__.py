"""
**Events**

- 2017-11-15 [0.2.2] update document of project
- 2017-10-14 move to another github project
- 2017-06-25 add function system.clear
- 2017-06-23 add function system.getch
- 2017-06-23 Support python3
- 2017-06-23 Add TestCase
"""

from __future__ import absolute_import

from dandan import error
from dandan import query
from dandan import system
from dandan import traffic
from dandan import value
from dandan import utils

__all__ = [
    "error",
    "query",
    "system",
    "traffic",
    "value",
    "utils",
]

__version__ = ".".join(
    [str(var) for var in
        [
            0,
            2,
            2,
    ]
    ])

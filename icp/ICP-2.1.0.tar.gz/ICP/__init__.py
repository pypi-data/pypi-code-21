#!/usr/bin/env python

import sys

if sys.version_info[0] == 3:
    from ICP.ICP import __version__
    from ICP.ICP import __author__
    from ICP.ICP import __date__
    from ICP.ICP import __url__
    from ICP.ICP import __copyright__
    from ICP.ICP import ICP
else:
    from ICP import __version__
    from ICP import __author__
    from ICP import __date__
    from ICP import __url__
    from ICP import __copyright__
    from ICP import ICP





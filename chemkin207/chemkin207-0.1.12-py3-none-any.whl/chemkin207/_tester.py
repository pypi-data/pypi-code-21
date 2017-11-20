import os
import sys

BASE_PATH = os.path.dirname(os.path.dirname(__file__))

def test():
    try:
	    import pytest
    except ImportError:
	    raise ImportError("You need pytest>=3.0 to run these tests")
    cmd = [BASE_PATH+'/chemkin207']
    print("running: pytest {}".format(cmd))
    sys.exit(pytest.main(cmd))

__all__ = ['test']

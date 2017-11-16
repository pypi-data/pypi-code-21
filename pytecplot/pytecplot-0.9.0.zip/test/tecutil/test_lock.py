import sys
import unittest
from unittest.mock import patch, Mock

from tecplot.tecutil import _tecutil
import tecplot

from .. import skip_if_connected

_is_locked = False


class TestLock(unittest.TestCase):

    @skip_if_connected
    def test_lock(self):

        def lock(shutdown_implicit_recording):
            global _is_locked
            _is_locked = True

        def unlock():
            global _is_locked
            _is_locked = False

        with patch('tecplot.tecutil.tecutil_connector._tecutil.ParentLockStart',
                   Mock(side_effect=lock)):
            handle = 'tecplot.tecutil.tecutil_connector._tecutil.handle.'
            with patch(handle + 'tecUtilParentLockFinish',
                       Mock(side_effect=unlock)):
                @tecplot.tecutil.lock()
                def fn():
                    global _is_locked
                    self.assertTrue(_is_locked)
                    return _is_locked
                self.assertFalse(_is_locked)
                self.assertEqual(fn(), True)
                self.assertFalse(_is_locked)

        lock_count = _tecutil.handle.tecUtilLockGetCount()
        with tecplot.tecutil.lock():
            self.assertEqual(_tecutil.handle.tecUtilLockGetCount(),
                             lock_count + 1)

        if sys.version_info < (3, 3):
            vinfo = sys.version_info
            sys.version_info = (3, 4)
            reload(tecplot.tecutil.util)
            sys.version_info = vinfo


if __name__ == '__main__':
    from .. import main
    main()

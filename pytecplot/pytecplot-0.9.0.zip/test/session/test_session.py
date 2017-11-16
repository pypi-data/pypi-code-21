from __future__ import unicode_literals

import os

from contextlib import contextmanager
import unittest
from unittest.mock import patch, Mock

import tecplot as tp


@contextmanager
def patch_env(key, val=None):
    saved_val = os.environ.get(key, None)
    try:
        try:
            del os.environ[key]
        except KeyError:
            pass
        if val is not None:
            os.environ[key] = val
        yield
    finally:
        if saved_val is None:
            try:
                del os.environ['HOME']
            except KeyError:
                pass
        else:
            os.environ[key] = saved_val


class TestSession(unittest.TestCase):

    def test_stop(self):
        with patch('tecplot.tecutil.tecutil_connector.TecUtilConnector.stop',
                   Mock(return_value=True)):
            self.assertIsNone(tp.session.stop())

    def test_acquire_license(self):
        with patch('tecplot.tecutil.tecutil_connector.TecUtilConnector.acquire_license',
                   Mock(return_value=True)):
            self.assertIsNone(tp.acquire_license())

    def test_release_license(self):
        with patch(
                'tecplot.tecutil.tecutil_connector.TecUtilConnector.release_license',
                Mock(return_value=True)):
            self.assertIsNone(tp.release_license())


if __name__ == '__main__':
    from .. import main
    main()

from __future__ import with_statement

import os
import unittest
import warnings

from unittest.mock import patch, Mock

import tecplot as tp


class TestIPython(unittest.TestCase):

    def setUp(self):
        tp.new_layout()

    def test_show(self):
        with patch('IPython.display.display'):
            tp.extension.ipython.show()

            with patch('os.remove', Mock(side_effect=OSError)) as rm:
                with patch('tecplot.extension.ipython.log.warning', Mock()) as lg:
                    tp.extension.ipython.show()
                self.assertEqual(lg.call_count, 1)
            os.remove(rm.call_args[0][0])


if __name__ == '__main__':
    from .. import main
    main()

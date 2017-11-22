"""
Legalese
--------
Copyright (c) 2016 Genome Research Ltd.

Author: Christopher Harrison <ch12@sanger.ac.uk>

This file is part of HGI's common Python library

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation; either version 3 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
import unittest
from threading import Thread

from hgicommon.threading import CountingLock


class TestCountingLock(unittest.TestCase):
    """ Tests for `CountingLock` """
    def test_single_thread(self):
        lock = CountingLock()
        with lock:
            self.assertEqual(lock.waiting_to_acquire(), 0)

    def test_multi_threaded(self):
        lock = CountingLock()

        def try_to_acquire():
            with lock:
                pass

        with lock:
            num_threads = 5
            for _ in range(num_threads):
                Thread(target=try_to_acquire).start()

            self.assertEqual(lock.waiting_to_acquire(), num_threads)

if __name__ == '__main__':
    unittest.main()

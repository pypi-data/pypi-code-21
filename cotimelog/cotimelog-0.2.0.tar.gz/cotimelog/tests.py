# encoding: utf8

"""
Created on 2017.10.18

@author: yalei
"""

import os
import time
import random
import unittest
from logging import getLogger, INFO
from cotimelog import ConcurrentTimeRotatingFileHandler


class TestLog(unittest.TestCase):
    def test_log(self):
        base_dir = os.path.dirname(__file__)
        base_name = 'mylogfile%s.log' % int(random.random() * 100000)
        filename = os.path.join(base_dir, base_name)
        log = getLogger()
        logfile = os.path.abspath(filename)
        # Rotate log after 1 second
        rotateHandler = ConcurrentTimeRotatingFileHandler(logfile, mode="a", when="S", backupCount=5)
        log.addHandler(rotateHandler)
        log.setLevel(INFO)
        [log.info(str(i)) for i in range(10)]
        time.sleep(1)
        [log.info(str(i)) for i in range(10, 100)]

        # test last log
        files = [f for f in os.listdir(base_dir) if base_name in f and not f.endswith('lock')]
        self.assertTrue(len(files) == 2)
        # test last log
        last_log = open(filename).read()
        self.assertEqual(last_log.strip().split(), [str(i) for i in range(10, 100)])

        # test first log
        first_log_name = [i for i in files if i != base_name][0]
        first_log = open(os.path.join(base_dir, first_log_name)).read()
        self.assertEqual(first_log.strip().split(), [str(i) for i in range(10)])

        # remove logs
        [os.remove(os.path.join(base_dir, f)) for f in os.listdir(base_dir) if base_name in f]

if __name__ == '__main__':
    unittest.main()

###############################################################################
# (c) Copyright 2016 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
'''
Test for the ThreadPool manager

@author: Stefan-Gabriel CHITIC
'''
import os
import unittest
import logging
from time import sleep, time
from pprint import pprint

from lbinstall.extra.ThreadPoolManager import ThreadPool


class Test(unittest.TestCase):

    def setUp(self):
        self.thredPool = ThreadPool(5)

    def tearDown(self):
        pass

    def wait_delay(self, d):
        sleep(d)
        return ("sleeping for (%d)sec" % d)

    def testPoolManagement(self):
        # Generate delays
        delays = [1 for i in range(10)]

        # Add the jobs in bulk to the thread pool. Alternatively you could use
        # `pool.add_task` to add single jobs. The code will block here, which
        # makes it possible to cancel the thread pool with an exception when
        # the currently running batch of workers is finished.
        start = time()
        self.thredPool.map(self.wait_delay, delays)
        res = self.thredPool.get_results()
        end = time()
        diff = end - start
        self.assertEqual(len(res), 10, 'Test if all the results are present')
        for r in res:
            self.assertEqual(r['success'], True,
                             'Test if all the treads ended ok')
            self.assertEqual(r['result'], 'sleeping for (1)sec',
                             'Test the results of each thread')
        # With threads, we should have the execution time less than 10 seconds
        # (The toal amount of sleeps in the wait_delay function)
        # We should have more than 2 seconds
        is_diff_in_interval = diff > 2 and diff < 10
        self.assertEqual(is_diff_in_interval, True,
                         'Check excution time')

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testFindPackage']
    unittest.main()

"""Staxing test files - Actions."""

import time
import unittest

from random import randint
from selenium import webdriver
from staxing.actions import Actions

__version__ = '1.0.0'


class TestStaxingActions(unittest.TestCase):
    """Staxing case tests for the ActionChain sleep."""

    def setUp(self):
        """Pretest settings."""
        self.driver = webdriver.Chrome()
        self.action_chain = Actions(self.driver)

    def tearDown(self):
        """Test destructor."""
        try:
            self.action_chain.__del__()
            self.driver.__del__()
        except:
            pass

    def test_actions_wait_within_two_percent_accuracy_100(self):
        """Test ActionChain wait time is accurate."""
        sleep_length = randint(3, 8) / 1.0
        start_time = time.time()
        self.action_chain.wait(sleep_length).perform()
        end_time = time.time()
        duration = end_time - start_time
        assert(duration >= sleep_length * 0.98), \
            'Sleep shorter than expected: %s < %s' % \
            (duration, sleep_length * 0.98)
        assert(duration <= sleep_length * 1.02), \
            'Sleep longer than expected: %s > %s' % \
            (duration, sleep_length * 1.02)

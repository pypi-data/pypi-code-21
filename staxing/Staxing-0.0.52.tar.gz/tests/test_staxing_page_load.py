"""Staxing test files - Page Load."""

# import logging
# import pytest
import unittest

# from selenium.webdriver.remote.remote_connection import LOGGER
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome import options
from staxing.page_load import SeleniumWait
# from time import sleep

__version__ = '1.0.0'


class TestStaxingSeleniumWait(unittest.TestCase):
    """Staxing case tests for the page loading wait."""

    def setUp(self):
        """Pretest settings."""
        option_set = options.Options()
        option_set.add_argument("disable-infobars")
        option_set.add_experimental_option(
            'prefs', {
                'credentials_enable_service': False,
                'profile': {
                    'password_manager_enabled': False
                }
            }
        )
        self.driver = webdriver.Chrome(chrome_options=option_set)
        self.driver.implicitly_wait(0)
        self.wait = SeleniumWait(self.driver)

    def tearDown(self):
        """Test destructor."""
        try:
            self.driver.__del__()
            self.wait.__del__()
        except:
            pass

    def test_wait_for_page_load(self):
        """Verify successful waits."""
        self.driver.implicitly_wait(0)
        self.driver.get('http://deelay.me/1000/http://openstax.org/')
        # immediate element search should fail
        with self.assertRaises(NoSuchElementException):
            self.driver.find_element_by_id('main')

        self.driver.get('http://deelay.me/1000/http://openstax.org/')
        # yield execution until the page is stale and content is loaded
        self.wait.wait_for_page_load()
        self.driver.find_element_by_id('main')

    def test_wait_for_loading_staleness(self):
        """Test for loading staleness."""
        self.driver.implicitly_wait(15)
        self.driver.get('http://www.ikea.com/us/en/')
        assert(self.wait.wait_for_loading_staleness(_id='SlideIndiacator')), \
            'transition not stale'
        pass

    def test_is_pseduo_valid(self):
        """Validate the pseudo selectors."""
        self.driver.get(
            'https://developer.mozilla.org/en-US/docs/Web/CSS/Pseudo-elements'
        )
        pseudos = self.driver.find_elements_by_css_selector(
            '#Index_of_pseudo-elements + ul > li code'
        )
        for i, _ in enumerate(pseudos):
            pseudos[i] = pseudos[i].get_attribute('innerHTML')
        for pseudo in pseudos:
            assert(self.wait.is_valid_pseudo(pseudo)), \
                '%s is not a valid pseudo element' % pseudo

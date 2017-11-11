'''!
@author atomicfruitcake

This module contains example tests to demonstrate how selepy
can be used for browser based automated testing
'''
import unittest

from selepy.selepy.common import constants
from ..common import driver, driver_funcs, driver_handler


class ExampleTestWithDriverObject(unittest.TestCase):
    '''
    This class contains example tests to demonstrate how selepy can be used to perform tests
    with both the 'Driver' object as with using the test wrapper
    '''
    def example_google_test_with_driver_object(self):
        '''
        An example of test performing a google search using a driver object
        '''
        Driver = driver.Driver()

        Driver.go_to_url(url=constants.constants.GOOGLE)
        Driver.send_keys_by_id(id='lst-ib', keys='do a barrel roll')
        Driver.click_element_by_xpath(xpath='//*[@value="Google Search"][1]')
        Driver.quit_driver()

    @driver_handler.wrap_test(driver_handler.startup, driver_handler.teardown)
    def example_google_test_with_wrapper(self):
        '''
        And example test performing a google search using a wrapper
        @return:
        '''
        driver_funcs.go_to_url(driver=driver, url=constants.constants.GOOGLE)
        driver_funcs.send_keys_by_id(driver=driver, id='lst-ib', keys='do a barrel roll')
        driver_funcs.click_element_by_xpath(driver=driver, xpath='//*[@value="Google Search"][1]')

if __name__ == '__main__':
    unittest.main()

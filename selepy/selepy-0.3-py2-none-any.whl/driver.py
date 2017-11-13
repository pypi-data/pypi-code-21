'''!
@author atomicfruitcake

This module encapusulates the driver handler and driver funcs
into a class, allowing the running of multiple Driver classes
to perform testing in parallel
'''
import driver_funcs as df
import driver_handler
from constants import constants


class Driver():
    '''
    Driver object to be perform the browser manipulation
    '''
    def __init__(self):
        self.driver = driver_handler.get_driver()

    def go_to_url(self, url):
        '''
        Sends the driver to a given url
        @param url: URL for driver to go to (e.g. https://www.google.co.uk/)
        '''
        df.go_to_url(driver=self.driver, url=url)

    def wait(self, seconds):
        '''
        Makes a driver wait for given number of seconds
        If seconds is None, defaults to the time set in constants.py
        @param seconds: number of seconds to wait for
        '''
        df.wait(seconds=seconds)

    def quit_driver(self):
        '''
        Quits a selenium driver. If driver is running in
        docker, it stops the docker containers. This command
        will render the driver as Type None
        '''
        df.quit_driver(driver=self.driver)

    def take_screenshot(self, filename):
        '''
        Takes a screenshot of the current page the driver is one.
        If using Docker, this does not work is browser is not debug mode
        @param filename: filename to save the screenshot as
        '''
        df.take_screenshot(driver=self.driver, filename=filename)

    def get_url(self):
        '''
        Gets the current url the driver is on
        @return: url - string url the driver is on
        '''
        return self.driver.current_url

    def assert_url(self, url):
        '''
        Asserts the driver is at a given URL
        @param url: URL to assert the driver is currently on
        @return:
        '''
        df.assert_url(self, url=url)

    def assert_url_contain(self, match_term):
        '''
        Asserts the driver's current url contains a given match term
        @param match_term: Term to assert is in the browser
        '''
        df.assert_url_contain(driver=self.driver, match_term=match_term)

    def click_element_by_id(self, id):
        '''
        Clicks a given element on the page the driver is on for a given id
        @param id: id of element to be clicked
        '''
        df.click_element_by_id(driver=self.driver, id=id)

    def click_element_by_xpath(self, xpath):
        '''
        Clicks a given element on the page the driver is on for a given xpath
        @param xpath: xpath of element to be clicked
        '''
        df.click_element_by_xpath(driver=self.driver, xpath=xpath)

    def click_element_by_name(self, name):
        '''
        Clicks a given element on the page the driver is on for a given name
        @param name: name of element to be clicked
        '''
        df.click_element_by_name(driver=self.driver, name=name)

    def send_keys_by_id(self, id, keys):
        '''
        Sends keys to a given element on the page the driver is on for a given id
        @param id: id of the element to send keys to
        @param keys: keys to send to the element
        '''
        df.send_keys_by_id(driver=self.driver, id=id, keys=keys)

    def send_keys_by_xpath(self, xpath, keys):
        '''
        Sends keys to a given element on the page the driver is on for a given xpath
        @param xpath: xpath of the element to send keys to
        @param keys: keys to send to the element
        '''
        df.send_keys_by_xpath(driver=self.driver, xpath=xpath, keys=keys)

    def send_keys_by_name(self, name, keys):
        '''
        Sends keys to a given element on the page the driver is on for a given name
        @param name: name of the element to send keys to
        @param keys: keys to send to the element
        '''
        df.send_keys_by_name(driver=self.driver, name=name, keys=keys)

if __name__ == '__main__':

    driver = Driver()

    driver.go_to_url(url=constants.GOOGLE)


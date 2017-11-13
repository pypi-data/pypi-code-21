'''!
@author atomicfruitcake

This module contains functions to manipulate selenium webdrivers
'''
import logging
import re
import time
from datetime import datetime

import selenium_docker_container
from constants import constants

logger = logging.getLogger(__name__)
logging.getLogger().addHandler(logging.StreamHandler())


def go_to_url(driver, url):
    '''
    Quits a selenium driver
    @param driver: driver to direct to url
    @param url: url to go to
    '''
    logger.info('Going to url {}'.format(url))

    driver.get(url)

def wait(seconds):
    '''
    Makes a driver wait for given number of seconds
    If seconds is None, defaults to the time set in constants.py
    @param seconds: number of seconds to wait for
    '''
    if seconds is None:
        seconds = constants.WAIT_TIME
    time.sleep(seconds)

def quit_driver(driver=None):
    '''
    Quits a selenium driver. If driver is running in
    docker, it stops the docker containers.
    @param driver: selenium driver to quit
    '''
    logger.info('Quitting {} driver'.format(driver))

    if driver is not None:
        driver.quit()

    if constants.DOCKER is True:
        selenium_docker_container.stop_docker()


def take_screenshot(driver, filename=None):
    '''
    Takes a screenshot of the screen of the current driver
    @param driver: driver to take screenshot of.
    @param filename: filename of the screenshot
    '''
    if filename is None:
        filename = str(datetime.utcnow())

    driver.get_screenshot_as_file(constants.SCREENSHOT_DIR + filename + '.png')

def assert_url(driver, url):
    '''
    Asserts that the drivers url ma
    @param driver: driver to assert url of
    @param url: string of url to assert is equal to that of driver
    '''
    logger.info('Asserting current url is {}'.format(url))

    assert driver.current_url == url

def assert_url_contain(driver, match_term):
    '''
    Asserts that the drivers url contains the specific term
    @param driver: driver to assert url contains a given string
    @param match_term: string we are asserting is contained in the url
    '''
    logger.info('Asserting current url contains {}'.format(match_term))
    assert re.search(match_term, driver.current_url) is True

def click_element_by_id(driver, id):
    '''
    Click an element based on id
    @param driver: driver with element to click
    @param id: id of element to click
    '''
    driver.find_element_by_id(id).click()

def click_element_by_xpath(driver, xpath):
    '''
    Click an element based on xpath
    @param driver: driver with element to click
    @param xpath: xpath of element to click
    '''
    driver.find_element_by_xpath(xpath).click()

def click_element_by_name(driver, name):
    '''
    Click an element based on name
    @param driver: driver with element to click
    @param name: name of element to click
    '''
    driver.find_element_by_name(name).click()

def send_keys_by_id(driver, id, keys):
    '''
    Send keys to an element based on id
    @param driver: driver with element send text to
    @param id: id of element to send keys to
    @param keys: string of keys to send
    '''
    driver.find_element_by_id(id).send_keys(keys)

def send_keys_by_xpath(driver, xpath, keys):
    '''
    Send keys to an element based on xpath
    @param driver: driver with element send text to
    @param xpath: xpath of element to send keys to
    @param keys: string of keys to send
    '''
    driver.find_element_by_xpath(xpath).send_keys(keys)

def send_keys_by_name(driver, name, keys):
    '''
    Send keys to an element based on name
    @param driver: driver with element send text to
    @param name: name of element to send keys to
    @param keys: string of keys to send
    '''
    driver.find_element_by_name(name).send_keys(keys)

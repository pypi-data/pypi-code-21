import json
import time
import sys

driver = None
javaExceptionWaitTime = 10

def setDriver(_driver):
    global driver
    driver = _driver

def getTiming():
    for x in range(1, javaExceptionWaitTime):
        try:
            return json.loads(driver.execute_script("return JSON.stringify(window.performance.timing)"))
        except Exception:
            time.sleep(1)
    raise ValueError('JavaScrip error in ' + sys._getframe().f_code.co_name)


def getResources():
    for x in range(1, javaExceptionWaitTime):
        try:
            return json.loads(driver.execute_script("return JSON.stringify(window.performance.getEntriesByType('resource'))"))
        except Exception:
            time.sleep(1)
    raise ValueError('JavaScrip error in ' + sys._getframe().f_code.co_name)


def getNbrOfResources():
    for x in range(1, javaExceptionWaitTime):
        try:
            return driver.execute_script("return window.performance.getEntriesByType('resource').length")
        except Exception:
            time.sleep(1)
    raise ValueError('JavaScrip error in ' + sys._getframe().f_code.co_name)


def clearResourceTimings():
    for x in range(1, javaExceptionWaitTime):
        try:
            return driver.execute_script("return window.performance.clearResourceTimings()")
        except Exception:
            time.sleep(1)
    raise ValueError('JavaScrip error in ' + sys._getframe().f_code.co_name)


def getAttributes(element):
    for x in range(1, javaExceptionWaitTime):
        try:
            return driver.execute_script("var items = {}; "
                                 "for (index = 0; index < arguments[0].attributes.length; ++index) "
                                 "{ items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; "
                                 "return items;"
                                 , element)
        except Exception:
            time.sleep(1)
    raise ValueError('JavaScrip error in ' + sys._getframe().f_code.co_name)


def unixTimeStamp():
    for x in range(1, javaExceptionWaitTime):
        try:
            return driver.execute_script("return Date.now()")
        except Exception:
            time.sleep(1)
    raise ValueError('JavaScrip error in ' + sys._getframe().f_code.co_name)

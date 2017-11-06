import json
import time
import hashlib
from datetime import datetime
from selenium.common.exceptions import *
from framewalker import DB
from framewalker import JavaScript

driver = None
transactionTimeStamp = ''
mainNavigationStart = 0
testRun = None
transaction = None
iteration = 0
waitForLoadedTimeOut = 0
waitForLoadedInsterval = 0
verbosity = 0
resourceFilter = []
frameFilter = []
consoleLog = False


#-----------Init and setters-----------#

def init(_driver, _product, _release, _comment, _verbosity=3, _waitForLoadedTimeOut=60, _waitForLoadedInsterval=3, _resourceFilter=None, _frameFilter=None, _consoleLog=False):
    global testRun
    global driver
    global waitForLoadedTimeOut
    global waitForLoadedInsterval
    global verbosity
    global resourceFilter
    global frameFilter
    global consoleLog
    driver = _driver
    JavaScript.setDriver(driver)
    testRun = DB.insertTestRun(timeStamp(), _product, _release, _comment)
    waitForLoadedTimeOut = _waitForLoadedTimeOut
    waitForLoadedInsterval = _waitForLoadedInsterval
    verbosity = _verbosity
    resourceFilter = _resourceFilter
    frameFilter = _frameFilter
    consoleLog = _consoleLog

def setDriver(_driver):
    global driver
    driver = _driver
    JavaScript.setDriver(driver)

def setIteration(iterationNumber):
    global iteration
    iteration = iterationNumber

def increaseIteration():
    global iteration
    iteration += 1

def setLoadInterval(loadinterval):
    global waitForLoadedInsterval
    waitForLoadedInsterval = loadinterval

#-----------Main functions-----------#

def report(transactionName):
    global transaction
    if verbosity > 0:
        transaction = DB.insertTransaction(testRun.test_run_id, timeStamp(), transactionName, iteration)
        driver.switch_to.default_content()
        timing = waitForTimingReady()
        saveFrame(timing, {'src': driver.current_url}, '0')
        saveIFrames('0')
        JavaScript.clearResourceTimings()
        driver.switch_to.default_content()
        if not frameFilter is None and len(frameFilter) > 0:
            DB.filterFrames(transaction, frameFilter)
        if DB.transactionHasFrames(transaction):
            DB.addTransactionTimes(transaction)
            DB.addFrameTimes(transaction)
            DB.addTimingTimes(transaction)
            if verbosity == 3:
                if not frameFilter is None and len(resourceFilter) > 0:
                    DB.filterResources(transaction, resourceFilter)
                DB.addResourceTimes(transaction)
    if consoleLog:
        printLog(transactionName, iteration)

def printLog(transactionName, iteration):
    template = "{0:5}{1:30}{2:10}"
    time = (DB.TransactionTime(transaction.transaction_id))
    Red = '\033[91m'
    Black = '\033[90m'
    Yellow = '\033[93m'
    if iteration == 1:
        color = Red
    elif time == -1:
        color = Yellow
    else:
        color = Black
    print(color + template.format(str(iteration), transactionName, str(time)))


def saveFrame(timing, attributes, frameStructureId):
    src = attributes.get('src')
    if DB.frameAlreadyExist(testRun, iteration, timing):
        if JavaScript.getNbrOfResources() > 0:
            frame = DB.insertFrame(transaction.transaction_id, '{' + frameStructureId + '}', truncatedSRC(src), hashedSRC(src), json.dumps(attributes))
            resources = waitForResourcesReady(timing)
            saveResources(frame, resources)
    else:
        if src is not None:
            frame = DB.insertFrame(transaction.transaction_id, '{' + frameStructureId + '}', truncatedSRC(src), hashedSRC(src), json.dumps(attributes))
            saveTiming(frame, timing)
            if verbosity == 3:
                resources = waitForResourcesReady(timing)
                saveResources(frame, resources)


def saveIFrames(frameStructureId):
    try:
        iFrames = driver.find_elements_by_tag_name('iframe')
    except NoSuchElementException:
        return
    for nbr, iFrame in enumerate(iFrames):
        recFrameStructureId = frameStructureId + "," + str(nbr)
        try:
            attributes = JavaScript.getAttributes(iFrame)
            driver.switch_to.frame(iFrame)
        except Exception:
            JavaScript.clearResourceTimings()
            return
        timing = waitForTimingReady()
        saveFrame(timing, attributes, recFrameStructureId)
        JavaScript.clearResourceTimings()
        currentWindow = driver.current_window_handle
        saveIFrames(recFrameStructureId)
        driver.switch_to.window(currentWindow)

#-----------Help Functions-----------#

def waitForTimingReady():
    time.sleep(1)
    for x in range(1, int(waitForLoadedTimeOut)):
        timing = getTiming()
        connectEnd = timing['loadEventEnd']
        if connectEnd != 0:
            return timing
        time.sleep(1)
    return None


def waitForResourcesReady(timing):
    if JavaScript.getNbrOfResources() == 0:
        return None
    for x in range(1, int(waitForLoadedTimeOut)):
        unixTime = JavaScript.unixTimeStamp()
        resources = getResources(timing)
        a = max(resources, key=lambda x:x['resource_absolute_end_time'])
        if unixTime - a['resource_absolute_end_time'] > waitForLoadedInsterval*1000:
            return resources
        time.sleep(1)
    return None


def getTiming():
    timing = JavaScript.getTiming()
    timing['timing_redirect'] = timing['fetchStart']-timing['navigationStart']
    timing['timing_appcache'] = timing['domainLookupStart'] - timing['fetchStart']
    timing['timing_dns'] = timing['domainLookupEnd'] - timing['domainLookupStart']
    timing['timing_dnstcp'] = timing['connectStart'] - timing['domainLookupEnd']
    timing['timing_tcp'] = timing['connectEnd'] - timing['connectStart']
    timing['timing_blocked'] = timing['requestStart'] - timing['connectEnd']
    timing['timing_request'] = timing['responseStart'] - timing['requestStart']
    timing['timing_dom'] = timing['domComplete'] - timing['responseStart']
    timing['timing_onload'] = timing['loadEventEnd'] - timing['domComplete']
    timing['timing_time'] = timing['loadEventEnd'] - timing['navigationStart']
    return timing


def getResources(timing):
    resources = JavaScript.getResources()
    res = []
    for d in resources:
        r={}
        r['resource_absolute_start_time'] = int(timing['navigationStart']) + int(d['startTime'])
        r['resource_absolute_end_time'] = r['resource_absolute_start_time'] + int(d['duration'])
        r['resource_time'] = d.pop('duration')
        r['resource_name'] = d.pop('name')
        r['resource_start_time'] = d.pop('startTime')
        del d['entryType']
        res.append(r)
    return res


def saveTiming(frame, timing):
    DB.insertTiming(frame.frame_id, timing)


def saveResources(frame, resources):
    DB.insertRecources(frame.frame_id, resources)

#-----------Misc-----------#

def hashedSRC(src):
    return hashlib.md5(src.encode('utf-8')).hexdigest()[:12]


def truncatedSRC(src):
    if len(src) > 50:
        src = src[:23] + '....' + src[-23:]
    return src


def timeStamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
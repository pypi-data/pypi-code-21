from time import sleep
from datetime import datetime as DT, timedelta
import threading
import bs4
from PyQt4.QtCore import *
from folstools import report_error, time_now
from folstools import myrequests, myprint
from folstools.myutils import mytry
# from folstools.myutils import notry as mytry


def check_error(func):
    def _check(self, *args, **kwargs):
        try:
            func(self, *args, **kwargs)
        except:
            report_error()
            self.fatal_error.emit()
    return _check


def make_date(timestr):
    today = DT.today().strftime('%Y-%m-%d')
    return DT.strptime(today + ' ' + timestr, '%Y-%m-%d %H:%M:%S')


def bsoup(text):
    return bs4.BeautifulSoup(text, 'html.parser')


class FailToGetResult(Exception):
    pass


class BetInfo(QObject):
    callback = pyqtSignal()
    fatal_error = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._fetch_result_timer = None

    @check_error
    def init(self, next_open, time_delta=timedelta(0, 300)):
        self._next_open_date = next_open
        self._time_delta = time_delta
        for __ in range(self._fetchResultRetry()):
            with mytry(lambda: self._switchLine()):
                self._all_results = self._fetchWebResult(False)
                break
        else:
            raise FailToGetResult
        if ((DT.now() - self.getResultDate(self.getLatestResult()))
           .total_seconds() < self._initTimeTolerance()):
            self._afterFetchResult(True)
        else:
            self._fetchLatestResult()

    def getNextOpenDate(self):
        return self._next_open_date

    def getAllResults(self):
        return self._all_results

    def getLatestResult(self):
        return self._all_results[0] if self._all_results else []

    def stopFetchResult(self):
        if self._fetch_result_timer:
            self._fetch_result_timer.cancel()

    def formatResult(self, result):
        return str(result)

    def getResultDate(self, result):
        print('getResultDate not override !!!!!!!')
        return None

    @check_error
    def _fetchLatestResult(self):
        new_result = False
        print('Getting results at ' + time_now())
        for __ in range(self._fetchResultRetry()):
            with mytry(lambda: self._switchLine()):
                latest_result = self._fetchWebResult(True)
                if latest_result != self.getLatestResult():
                    new_result = True
                    self._all_results.insert(0, latest_result)
                    print(self.formatResult(latest_result))
                    break
                if ((DT.now() - self.getResultDate(latest_result))
                   .total_seconds() < self._fetchResultTimeTolerance()):
                    break
                self._switchLine()
        else:
            raise FailToGetResult
        self._afterFetchResult(new_result)

    def _switchLine(self):
        myprint('No line available, just sleep 2 seconds')
        sleep(2)

    def _afterFetchResult(self, new_result):
        self._renewNextOpenDate()
        print('Setup timer at ' + time_now())
        self._fetch_result_timer = threading.Timer(
            ((self._next_open_date - DT.now())
             .total_seconds()), self._fetchLatestResult)
        self._fetch_result_timer.start()
        if new_result:
            self.callback.emit()

    def _renewNextOpenDate(self):
        now = DT.now()
        while self._next_open_date < now:
            self._next_open_date += self._time_delta

    def _fetchResultRetry(self):
        return 30

    def _initTimeTolerance(self):
        return 100000  # default big enough

    def _fetchResultTimeTolerance(self):
        return 0  # default small enough

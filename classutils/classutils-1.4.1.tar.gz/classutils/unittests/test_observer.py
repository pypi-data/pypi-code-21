import sys
import unittest

from classutils.observer import (Observable,
                                 ObserverError)


class CheckObservable(Observable):
    pass


class ObserverNoNotify():
    pass


class Observer():
    def notify(self,
               *args,
               **kwargs):
        pass

class TestObserver(unittest.TestCase):

    def test_x(self):
        co = CheckObservable()

        co.register_observer(Observer())
        try:
            co.register_observer(ObserverNoNotify())
            raise AssertionError(u'ObserverError not thrown')
        except ObserverError:
            pass

if __name__ == u'__main__':
    unittest.main()

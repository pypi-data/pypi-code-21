from builtins import object
import sys
import time
import traceback
from junit_xml import TestCase, TestSuite
import logging
logging.basicConfig(level=logging.INFO)


def xunit_suite(name, cases):
    return TestSuite(name, [case._tc for case in cases])


def xunit_dump(suites):
    return TestSuite.to_xml_string(suites)


class xunit(object):
    def __init__(self, name, classname):
        self._name = name
        self._classname = classname
        self._tc = None

    def __enter__(self):
        self._start = time.time()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._end = time.time()
        tc = TestCase(self._name, self._classname,
                      self._end - self._start, '', '')
        if exc_type:
            logging.warn(exc_value)

            tc.add_failure_info(message=exc_value, output='\n'.join(
                traceback.format_exception(exc_type, exc_value,
                                           exc_traceback)))
        self._tc = tc

        # If an exception is supplied, and the method wishes to suppress the
        # exception (i.e., prevent it from being propagated), it should return
        # a true value. Otherwise, the exception will be processed normally
        # upon exit from this method.
        return self


if __name__ == '__main__':
    with xunit('apollo', 'test.pass') as tc1:
        pass

    with xunit('apollo', 'test.fail') as tc2:
        raise Exception("bad things happened")

    with xunit('apollo', 'test.second') as tc3:
        time.sleep(1)

    ts = xunit_suite('Context management tests', [tc1, tc2, tc3])
    sys.stdout.write(xunit_dump([ts]))

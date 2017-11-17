# metadata
__version__ = '4.0.0'
__author__ = 'Cisco Systems'
__contact__ = 'pyats-support-ext@cisco.com'
__copyright__ = 'Copyright (c) 2017, Cisco Systems Inc.'

# expose internal modules
from .counter import ResultCounter
from .result import TestResult
from .context import TestResultContext, RootTestResultContext, \
                     get_result_context, update_test_result

# limited the # of exports
# (do not export Null)
__all__ = ['Failed', 'Passed', 'Aborted', 'Blocked', 'Skipped',
           'Errored', 'Passx']


# create generic result codes
Failed  = TestResult(0)
Passed  = TestResult(1)
Aborted = TestResult(2)
Blocked = TestResult(3)
Skipped = TestResult(4)
Errored = TestResult(5)
Passx   = TestResult(8)
Null   = TestResult(99)

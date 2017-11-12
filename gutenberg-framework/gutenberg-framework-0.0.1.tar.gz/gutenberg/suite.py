from gutenberg.core import AssertionException;

_failureCount = 0;
_testCount = 0;

def Test(testFunction):
    global _testCount;
    global _failureCount;
    _testCount += 1;
    try:
        testFunction();
        print("{} : {} -> OK".format(_testCount, testFunction.__name__));
    except AssertionException as e:
        print("{} : {} -> Completed with errors.".format(_testCount, testFunction.__name__));
        print(e);
        _failureCount += 1;

def done():
    if (_failureCount == 0):
        print("Completed {} tests without errors.".format(_testCount));
    else:
        print("Completed {} tests. There were {} errors.".format(_testCount, _failureCount));

def Case(caseFunction):
    print("Test case : {}".format(caseFunction.__name__));
    global _failureCount;
    global _testCount;
    _failureCount = 0;
    _testCount = 0;
    caseFunction();
    done();

import unittest

from utils import test_functions 
from utils import test_jsonizable 
from resources import test_job
from resources import test_image
from resources import test_cluster
from client import test_response

def suite():
    load = unittest.TestLoader().loadTestsFromModule
    modules = [
        test_job,
        test_image,
        test_cluster,
        test_functions,
        test_jsonizable,
    ]
    suites = unittest.TestSuite(map(load, modules))
    return suites

if __name__ == '__main__':
    s = suite()
    unittest.TextTestRunner(verbosity=2).run(s)

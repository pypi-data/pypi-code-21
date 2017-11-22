import unittest
from containers import container_suite

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'


unittest.TextTestRunner(verbosity=2, failfast=True).run(container_suite)

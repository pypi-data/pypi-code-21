
import unittest


loader = unittest.TestLoader()
suite = loader.discover('TestCase', pattern='Test*.py')
unittest.TextTestRunner().run(suite)



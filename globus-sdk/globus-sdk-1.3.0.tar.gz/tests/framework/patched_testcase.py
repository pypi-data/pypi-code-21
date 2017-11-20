import unittest


class PatchedTestCase(unittest.TestCase):
    """
    A class of TestCases which have a number of patches applied at setUp time
    and removed at tearDown time. Defining this all in one place makes layering
    multiple sets of mock patches much easier, as they can just add their
    desired patches to the set.
    The alternative is for every test class that wants to define a set of setUp
    and tearDown patches to define its own redundant setUp and tearDown.
    """
    def __init__(self, desc):
        unittest.TestCase.__init__(self, desc)

        # a set of patches held by the class instance -- these are expected to
        # be results of mock.patch() invocations
        self._patches = set()

    def setUp(self):
        """
        Start all desired mocking
        """
        for p in self._patches:
            p.start()

    def tearDown(self):
        """
        Remove all of the patches so that a clean set can be applied
        """
        for p in self._patches:
            p.stop()

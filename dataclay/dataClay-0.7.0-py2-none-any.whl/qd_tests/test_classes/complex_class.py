import numpy as np

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'


class PartOne(object):
    """An integer basic type.

    @dclayProperty int prop
    """
    def __init__(self):
        """Initialization.
        @dclayMethodReturn None
        """
        self.prop = 42

    def set_val(self, val):
        """Initialization.
        @dclayMethodParameter int val
        @dclayMethodReturn None
        """
        self.prop = val

    def get_val(self):
        """Initialization.
        @dclayMethodReturn int
        @dclayMethodReadOnly
        """
        return self.prop


class PartTwo(object):
    """Two opaque `blobs`.

    @dclayProperty anything b1
    @dclayProperty anything b2
    """
    def __init__(self):
        """Initialization.
        @dclayMethodReturn None
        """
        import numpy as np
        self.b1 = "This is something"
        self.b2 = np.array([[1, 2], [2, 3], [3, 4], [4, 5]])


class ComplexClass(object):
    """Class containing Python classes.

    @dclayProperty test_classes.complex_class.PartOne pt1
    @dclayProperty test_classes.complex_class.PartTwo pt2
    """
    def __init__(self):
        """Initialization.

        @dclayMethodReturn None
        """
        self.pt1 = PartOne()
        self.pt2 = PartTwo()

    def get_pt1(self):
        """Blah
        @dclayMethodReturn test_classes.complex_class.PartOne
        @dclayMethodReadOnly
        """
        return self.pt1

    def get_pt2(self):
        """Blah
        @dclayMethodReturn test_classes.complex_class.PartTwo
        @dclayMethodReadOnly
        """
        return self.pt2

    def get_pt1_prop(self):
        """Blah
        @dclayMethodReturn int
        @dclayMethodReadOnly
        """
        return self.pt1.get_val()

    def set_pt1(self, new_pt1):
        """
        @dclayMethodParameter test_classes.complex_class.PartOne new_pt1
        @dclayMethodReturn None
        """
        self.pt1 = new_pt1


class ChainLink(object):
    """
    @dclayProperty test_classes.complex_class.ChainLink previous
    @dclayProperty test_classes.complex_class.ChainLink next
    """
    def __init__(self):
        """
        @dclayMethodReturn None
        """
        self.previous = None
        self.next = None

    def do_fibonacci(self, value1, value2):
        """
        @dclayMethodParameter int value1
        @dclayMethodParameter int value2
        @dclayMethodReturn int
        """
        print "do_fibonacci at %r" % self
        if self.next:
            val = self.next.do_fibonacci(value2, value1+value2)
        else:
            val = value1 + value2
        print "value:", val
        return val


class ChainedList(object):
    """
    @dclayImport test_classes.complex_class.ChainLink
    @dclayProperty chain list<>
    """
    def __init__(self, link_qty):
        """
        @dclayMethodParameter link_qty int
        @dclayMethodReturn None
        """
        self.chain = []

        for _ in range(link_qty):
            self.chain.append(ChainLink())

        for ch in self.chain:
            ch.make_persistent()

        for a, b in zip(self.chain[:-1], self.chain[1:]):
            a.next = b
            b.previous = a

    def start_fibonacci(self):
        """
        @dclayMethodReturn None
        """
        self.chain[0].do_fibonacci(1, 1)

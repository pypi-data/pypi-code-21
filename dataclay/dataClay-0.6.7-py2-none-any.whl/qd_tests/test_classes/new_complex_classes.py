from dataclay.managers.classes import DataClayObject, dclayMethod
import numpy as np

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'


class PartOne(DataClayObject):
    """An integer basic type.

    @dclayProperty prop int
    """
    @dclayMethod()
    def __init__(self):
        self.prop = 42

    @dclayMethod(val=int)
    def set_val(self, val):
        self.prop = val

    @dclayMethod(return_=int)
    def get_val(self):
        return self.prop


class PartTwo(DataClayObject):
    """Two opaque `blobs`.

    @dclayProperty b1 anything
    @dclayProperty b2 anything
    """
    @dclayMethod()
    def __init__(self):
        import numpy as np
        self.b1 = "This is something"
        self.b2 = np.array([[1, 2], [2, 3], [3, 4], [4, 5]])


class ComplexClass(DataClayObject):
    """Class containing Python classes.

    @dclayProperty pt1 test_classes.new_complex_classes.PartOne
    @dclayProperty pt2 test_classes.new_complex_classes.PartTwo
    """
    @dclayMethod()
    def __init__(self):
        self.pt1 = PartOne()
        self.pt2 = PartTwo()

    @dclayMethod(return_='test_classes.new_complex_classes.PartOne')
    def get_pt1(self):
        return self.pt1

    @dclayMethod(return_='test_classes.new_complex_classes.PartTwo')
    def get_pt2(self):
        return self.pt2

    @dclayMethod(return_=int)
    def get_pt1_prop(self):
        return self.pt1.get_val()

    @dclayMethod(new_pt1='test_classes.new_complex_classes.PartOne')
    def set_pt1(self, new_pt1):
        self.pt1 = new_pt1


class ChainLink(DataClayObject):
    """
    @dclayProperty previous test_classes.new_complex_classes.ChainLink
    @dclayProperty next_ test_classes.new_complex_classes.ChainLink
    """
    @dclayMethod()
    def __init__(self):
        self.previous = None
        self.next_ = None

    @dclayMethod(value1=int,
                 value2=int,
                 return_=int)
    def do_fibonacci(self, value1, value2):
        print "do_fibonacci at %r" % self
        if self.next_:
            val = self.next_.do_fibonacci(value2, value1+value2)
        else:
            val = value1 + value2
        print "value:", val
        return val


class ChainedList(DataClayObject):
    """
    @dclayImport test_classes.new_complex_classes.ChainLink
    @dclayProperty chain list<ChainLink>
    """
    @dclayMethod(link_qty=int)
    def __init__(self, link_qty):
        self.chain = []

        for _ in range(link_qty):
            self.chain.append(ChainLink())

        for a, b in zip(self.chain[:-1], self.chain[1:]):
            a.next_ = b
            b.previous = a

    @dclayMethod(return_=int)
    def start_fibonacci(self):
        """
        @dclayMethodReturn None
        """
        return self.chain[0].do_fibonacci(1, 1)

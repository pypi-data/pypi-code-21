__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'


class AlphaClass(object):
    """
    Compulsory DataClay documentation for class
    """
    pass


class BetaClass(object):
    """
    Compulsory DataClay documentation for class
    """
    def __init__(self):
        pass

    def print_something(self):
        """
        This is some DataClay documentation

        @dclayMethodReturn int
        @dclayMethodReadOnly
        """
        print "something"
        return 42


class GammaClass(object):
    """
    We announce the property, an integer basic type

    @dclayProperty int prop
    """
    def __init__(self):
        """
        Initialization
        @dclayMethodReturn None
        """
        self.prop = 42

    def do_plus_one(self):
        """
        :return: The property (once incremented)
        @dclayMethodReturn int
        """
        self.prop += 1
        print "Doing plus one, result:", self.prop
        return self.prop

    def do_minus_one(self):
        """
        :return: The property (once decremented)
        @dclayMethodReturn int
        """
        self.prop -= 1
        print "Doing minus one, result:", self.prop
        return self.prop
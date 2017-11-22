__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'


class PropertiesClass(object):
    """This class only holds properties.

    @dclayProperty int propInt
    @dclayProperty float propFloat
    @dclayProperty bool propBool
    """
    def __init__(self):
        """Initialization
        @dclayMethodReturn None
        """
        self.propInt = 42
        self.propFloat = 4.2
        self.propBool = True


class PrimitiveClass(object):
    """
    Announce the properties

    @dclayProperty propInt int
    @dclayProperty propFloat float
    @dclayProperty propBool bool
    @dclayProperty propBlob anything
    @dclayProperty propList list<>
    """

    def __init__(self):
        """
        Initialization
        @dclayMethodReturn None
        """
        import numpy
        self.propInt = 42
        self.propFloat = 4.2
        self.propBool = True
        self.propBlob = numpy.array([[1.23, 2.34], [2.11, 2.12], [123.123, 234.234]])
        self.propList = [None] * 7

    def getBlob(self):
        """
        :return: The Blob Property
        @dclayMethodReturn anything
        @dclayMethodReadOnly
        """
        print "At function getBlob"
        return self.propBlob

    def setBlob(self, blob):
        """
        @dclayMethodParameter val anything
        @dclayMethodReturn None
        """
        print "At function setBlob"
        self.propBlob = blob

    def getInt(self):
        """
        :return: The Integer Property
        @dclayMethodReturn int
        @dclayMethodReadOnly
        """
        print "At function getInt"
        return self.propInt

    def setInt(self, val):
        """
        :param val: The value to set
        :return: None
        @dclayMethodParameter val int
        @dclayMethodReturn None
        """
        print "At function setInt"
        self.propInt = val

    def getFloat(self):
        """
        :return: The Float Property
        @dclayMethodReturn float
        @dclayMethodReadOnly
        """
        print "At function getFloat"
        return self.propFloat

    def setFloat(self, val):
        """
        :param val: The value to set
        :return: None
        @dclayMethodParameter val float
        @dclayMethodReturn None
        """
        print "At function setFloat"
        self.propFloat = val

    def getList(self):
        """
        @dclayMethodReturn list<>
        @dclayMethodReadOnly
        """
        print "At function getList"
        return self.propList

    def setList(self, val):
        """
        @dclayMethodParameter val list<>
        @dclayMethodReturn None
        """
        print "At function setList"
        self.propList = val

    def getBool(self):
        """
        :return: The Boolean Property
        @dclayMethodReturn bool
        @dclayMethodReadOnly
        """
        print "At function getBool"
        return self.propBool

    def setBool(self, val):
        """
        :param val: The value to set
        :return: None
        @dclayMethodParameter val bool
        @dclayMethodReturn None
        """
        print "At function setBool"
        self.propBool = val

    def multiplyAdd(self, val1, val2, val3):
        """
        @dclayMethodParameter val1 float
        @dclayMethodParameter val2 float
        @dclayMethodParameter val3 float
        @dclayMethodReturn float
        @dclayMethodReadOnly
        """
        return val1*val2 + val3


class BlobbingClass(object):
    """
    Announce the properties

    @dclayProperty propDict anything
    @dclayProperty propBlob anything
    """

    def __init__(self):
        """
        Initialization
        @dclayMethodReturn None
        """
        import numpy
        self.propDict = {1: "one", 2: 2.0}
        self.propBlob = numpy.array([1, 2, 3])

    def getDictAsBlob(self):
        """
        :return: The Dictionary field, as a blob type
        @dclayMethodReturn anything
        @dclayMethodReadOnly
        """
        print "At function getDictAsBlob"
        return self.propDict

    def getBlob(self):
        """
        :return: The Blob field
        @dclayMethodReturn anything
        @dclayMethodReadOnly
        """
        print "At function getBlob"
        return self.propBlob

    def setBlob(self, val):
        """
        @dclayMethodParameter val anything
        @dclayMethodReturn None
        """
        print "At function setBlob"
        self.propBlob = val

    def setDictFromKWArgs(self, first, **kwargs):
        """
        :param first: The first element, an integer
        :param kwargs: The keyword arguments
        :return: None
        @dclayMethodParameter first int
        @dclayMethodReturn None
        """
        print "At function setDictFromKWArgs"
        self.propDict = kwargs
        self.propDict[first] = "first"

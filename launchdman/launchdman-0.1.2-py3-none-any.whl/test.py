import collections


def printAll(*args):
    print(list(flatten(args)))


def flatten(l):
    for el in l:
        if isinstance(
                el, collections.Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten(el)
        else:
            yield el


# printAll(23)

a = '''Label
Program
ProgramArguments
EnvironmentVariables
StandardInPath
StandardOutPath
StandardErrorPath
WorkingDirectory
SoftResourceLimit
HardResourceLimit
RunAtLoad
StartInterval
StartCalendarInterval
StartOnMount
WatchPaths
QueueDirecotries
KeepAlive
UserName
GroupName
InitGroups
Umask
RootDirecotry
AbandonProcessGroup
ExitTimeOut
Timeout
ThrottleInverval
LegacyTimers
Nice'''

a = a.split('\n')


def makeClass(l):
    output = ''
    for i in l:
        i = 'class {}():\n    pass\n\n\n'.format(i)
        output = output + i
    return output


def makeMethod(l):
    output = ''
    for i in l:
        iLowered = i.replace(i[0], i[0].lower())
        t = '    def {0}(self, *args):\n        condition = conditions.{1}(*args)\n        self.{0} = condition\n        self._add([self.{0}, self.value])\n\n'.format(
            iLowered, i)
        output = output + t
    return output


def makeProperty(l):
    output = ''
    for i in l:
        iLowered = i.replace(i[0], i[0].lower())
        t = '    @property    def {0}(self, *args):\n        condition = conditions.{1}(*args)\n        self.{0} = condition\n        self._add([self.{0}, self.value])\n\n'.format(
            iLowered, i)
        output = output + t
    return output


def makeAttribute(l):
    output = ''
    for i in l:
        t = '{0} = dic[\'{0}\']\n'.format(i)
        output = output + t
    return output


print(makeAttribute(a))

# print(makeMethod(a))


def makeDict(l):
    output = ''
    for i in l:
        t = "'{0}': conditions.{0}(),\n".format(i)
        output += t
    return output


# print(makeDict(a))


def aba(tag, *value):
    print('tag:', tag)
    print(value)
    map(print(), list(flatten(value)))


# aba('tag', 'value1', 'value2')


class AClass():
    def __init__(self):
        print(self.__class__.__name__)


class BClass(AClass):
    pass


class CClass(BClass):
    pass


# a = AClass()
c = CClass()

# print(makeClass(a))

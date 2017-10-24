from config import *


def singleStringTest():
    myStringSingle = StringSingle('wow')
    print(myStringSingle.printMe(myStringSingle.tag, myStringSingle.value))


def changeToTest():
    schedule = Label('com.yuan.app')
    schedule.changeTo('com.yohoho.app')
    print(schedule.printMe(schedule.key, schedule.value))


def ProgramTest():
    schedule = Program('/path/to/program')
    schedule.changeTo('/path/to/new/pragram')
    print(schedule.printMe(schedule.key, schedule.value))


def RunAtLoadTest():
    schedule = RunAtLoad()
    print(schedule.sub)


def JobTest():
    job = Job('/Users/yuan/Library/LaunchAgents/wtf.plist')
    job.add(RunAtLoad())
    job.add(Program('/Users/yuan/bin/churchpaper'))
    job.add(Label('com.yuan.wtf'))
    calendarSchedule = StartCalendarInterval()
    calendarSchedule.add(calendarSchedule.gen(day=2, hour=12))
    job.add(calendarSchedule)
    job.remove(calendarSchedule)
    print(job.printMe(job.tag, job.value))
    job.write()


# listA = ['something', 'some otherthing']

# def returnList(aList):
#     return aList

# anotherList = returnList(listA)

# anotherList.append('wow')
# print(listA)

# a = Single('bob')
# b = a
# aList = [a]
# bList = []
# bList.append(aList[0])

# print(bList[0] is aList[0])

# single1 = Single('tag1', '1', '2', '3', '4')
# ten = single1.add('10')[0]
# print(single1.value[4])
# print(ten is single1.value[4])
# print(single1.printMe(single1.tag, single1.value))
# single1.remove(ten)
# print(single1.printMe(single1.tag, single1.value))


def removeTest():
    single1 = Single('tag1', '10')
    single2 = Single('tag1', '10')
    single0 = Single('tag1', '10')
    single3 = Single('tag3', single2, single1, single0, single1)
    singleRemove = Single('tag1', '10')
    print(single1 == single2)
    print(single3.value)
    single3.remove(singleRemove)
    print(single3.value)
    single3.remove(singleRemove)
    print(single3.value)


def addTest():
    single101 = Single('tag1', 1, 2, 3, 4)
    single101.add(5, 6)
    print(single101.value)


def ProgramArgumentsTest():
    programArguments = ProgramArguments('/paht', '-r', '-m')
    print(
        programArguments.printMe(programArguments.key, programArguments.value))
    print('add')
    programArguments.add('new arg')
    print(
        programArguments.printMe(programArguments.key, programArguments.value))


def EnvironmentVariablesTest():
    schedule = EnvironmentVariables('PATH:PATH')
    print(schedule.printMe(schedule.key, schedule.value))
    schedule.changeTo('new/path')
    print(schedule.printMe(schedule.key, schedule.value))


def LabelTest():
    schedule = Label('label')
    print(schedule.printMe(schedule.key, schedule.value))


def SoftResourceLimitTest():
    schedule = SoftResourceLimit({'CPU': 123345, 'FileSize': 1024})
    print(schedule.value)
    print(schedule.parse())
    print(schedule.printMe(schedule.key, schedule.value))


def StartIntervalTest():
    schedule = StartInterval()
    schedule.every(2).minute
    print(schedule.parse())


def StartCalendarIntervalTest():
    schedule = StartCalendarInterval()
    # schedule.add(schedule.gen(day=1))
    # print('1st:\n' + schedule.parse())
    # schedule.remove(schedule.gen(day=1))
    # print('removed:\n' + schedule.parse())
    # schedule.add(
    #     schedule.gen(day=1, month=12, hour=9), schedule.gen(day=1, month=2))
    # print('complex:\n' + schedule.parse())

    # schedule.add(
    #     schedule.genInterval(day=(1, 3), hour=(8, 10), minute=(11, 15)))

    print(schedule.genMix(day=(1, 3, 6), hour=tuple(range(1, 21, 2))))
    schedule.add(schedule.genMix(day=(1, 3, 6), hour=(tuple(range(1, 21, 2)))))

    # print(schedule.genInterval(day=(1, 3), hour=(8, 10), minute=(11, 15)))
    print(schedule.parse())


def WatchPathsTest():
    schedule = WatchPaths('/path', 'path2')
    print(schedule.parse())


def KeepAliveTest():
    schedule = KeepAlive(depends, 'SuccessfullExit')
    schedule.addKey(PathState, '/tmp/runJob')
    schedule.removeKey(PathState, '/tmp/runJob')
    # schedule.add('SuccessfullExit', '2', '3')
    # schedule = KeepAlive(always)
    print(schedule.printMe(schedule.key, schedule.value))


# singleStringTest()
# changeToTest()
# ProgramTest()
# ProgramArgumentsTest()
# EnvironmentVariablesTest()
# LabelTest()
SoftResourceLimitTest()
# StartIntervalTest()
# StartCalendarIntervalTest()
# WatchPathsTest()

# KeepAliveTest()

# JobTest()

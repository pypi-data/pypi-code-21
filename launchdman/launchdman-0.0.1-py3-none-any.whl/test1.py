from conditions import *
import time


def returnTuple():
    return (1)
    print(type(returnTuple()))


def printAncestor(obj):
    ancestor = list(obj.__class__.__mro__)[-2]
    print(ancestor)
    print(ancestor is Single)


def tf():
    if ():
        print('() is True')
    if not ():
        print('() is False')
    if (0):
        print('(0) is True')
    if not (0):
        print('(0) is False')
    if (0) != ():
        print('works')


def genDictList(dic):
    # e.g. dic: {'month': (1,5), 'day': (2,4)}
    # return list: [[list of month], [list of day]]
    grandList = []
    for k in dic:
        # e.g. k: 'month', dic[k]: (1,5)
        l = []
        rangeTuple = (dic[k][0], dic[k][1] + 1)  # e.g. (1,6)
        for num in range(rangeTuple[0], rangeTuple[1]):  # e.g. 1, 2, 3, 4, 5
            d = {k: num}  # e.g. {'month': 1}
            l.append(d)  # e.g. [{'month': 1}, {'month': 2}]
        grandList.append(l)  # e.g. [[list of month], [list of day]]
    return grandList


def crossCombine(l):
    '''
    e.g.: l: [[{'month': 1}, {'month': 2}], [{'day': 2}, {'day': 3}, {'day': 4}]]
          l: [[dic of month], [dict of day]]
          l: [[a,a1,a2,...], [b,b1,b2,...]]
    combine return: [[a,b], [a,b1], [a,b2], [a1,b], [a1,b1], [a1, b2], [a2,b], [a2,b1], [a2,b2]]
    combineDict return: [{a,b}, {a,b1}, {a,b2}, {a1,b}, {a1,b1}, {a1, b2}, {a2,b}, {a2,b1}, {a2,b2}]


    '''
    resultList = []
    firstList = l[0]
    rest = l[1:]
    if len(rest) == 0:
        return firstList
    for e in firstList:
        for e1 in crossCombine(rest):
            resultList.append(combinetDict(e, e1))
    return resultList


def combine(a1, a2):
    if not isinstance(a1, list):
        a1 = [a1]
    if not isinstance(a2, list):
        a2 = [a2]
    return a1 + a2


def combinetDict(d, d1):
    return {**d, **d1}


# tf()
# dic = {'month': (1, 5), 'day': (2, 4)}
# l = [['a', 'a1', 'a2'], ['b', 'b1', 'b2'], ['c', 'c1', 'c2']]
# print(gen(dic))
# printAncestor(Single('tag1', 'value'))

# a1 = list(range(0, 10000)) + [[] * 1000]
# a2 = list(range(0, 1000))
# t = time.time()
# combine(a1, a2)
# print(crossCombine(genGrandDict(dic)))
# print(time.time() - t)


class A():
    def bark(self):
        print('bark!')


class B():
    pass


class C():
    def __init__(self):
        pass

    def changeToA(self):
        self.__class__ = A


c = C()
c.changeToA()
c.bark()
print(type(c))

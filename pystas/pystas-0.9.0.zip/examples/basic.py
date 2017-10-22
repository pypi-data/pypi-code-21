from pystas import logpista, logwargs, logw1arg
import random
import time


@logpista
def a_function_with_strange_behavior(bla):
    print 'will I crash?',
    if random.random() < 0.05:
        print 'yes..'
        raise Exception("bla")
    if random.random() < 0.05:
        print 'yes..'
        raise RuntimeError("shit")
    print 'no! :-)'


@logw1arg
def funcbyargs(arg1):
    time.sleep(arg1/20)


@logwargs
def funcbyallargs(arg1, arg2, arg3=None):
    time.sleep(0.1)


class SomeClass:
    @logpista
    def some_interesting_method(self):
        print 'hold on..'
        time.sleep(random.random()*3)

    @classmethod
    @logpista
    def AClassMethod(cls, var):
        print 'test'

    @staticmethod
    @logpista
    def AStaticMethod(var):
        print 'blablabla'


class NewClass(object):
    @logpista
    def simple_method(self):
        time.sleep(0.5)


SomeClass.AStaticMethod(3)
SomeClass.AClassMethod(15)
NewClass().simple_method()


for arg in [2, 4]:
    for x in xrange(5):
        funcbyargs(arg)

for arg in xrange(4):
    funcbyallargs(arg, str(arg), random.randint(0,4))

for x in xrange(random.randint(1, 7)):
    a_function_with_strange_behavior(2)
for x in xrange(random.randint(1, 2)):
    SomeClass().some_interesting_method()
for x in xrange(random.randint(1, 2)):
    a_function_with_strange_behavior(2)




from __future__ import absolute_import, division, print_function

from builtins import object

class Condition(object):
    def __init__(self, testfunc, reason, pass_value, neg_reason=None):
        self.__func = testfunc
        self.__msg = reason
        self.__pass_value = pass_value
        self.__neg_msg = neg_reason

    # python 2
    def __nonzero__(self):
        return self.Pass()

    # python 3
    def __bool__(self):
        return self.Pass()

    def Pass(self):
        return self.__pass_value == self.__func()

    @property
    def Message(self):
        return self.__msg

    # this is to help with cases like SkipIf(isPlatform(..))
    # where isPlatform would normal give a message that we
    # need to be platform X and we on platfom X to a different
    # message that we should not be platform X
    @property
    def NegitiveMessage(self):
        if self.__neg_msg is not None:
            return self.__neg_msg
        else:
            return self.__msg


class ConditionFactory(object):

    def __init__(self, variables, env):
        self.__variables = variables
        self.__env = env

    @property
    def Variables(self):
        return self.__variables

    @property
    def Env(self):
        return self.__env

    def __call__(self, function, reason, pass_value=True, neg_reason=None):
        return self.Condition(function, reason, pass_value, neg_reason)

    def Condition(self, function, reason, pass_value=True, neg_reason=None):
        '''This is a general function for any condition testing
        it takes a a function that will return true or false
        a message to report why this condition failed ( and as such we skipped the test)
        optional value to control if the return value of False should be used as a failure of
        the condition. defaults to True.. ie False is failure and True is passing.
        '''

        ret = Condition(function, reason, pass_value, neg_reason)
        return ret

    def true(self, msg):
        return self.Condition(lambda: True, msg, True)


class Conditions(object):
    """description of class"""

    def __init__(self):
        self.__condition_if = []
        self.__condition_unless = []
        self.__reason = None

    def _AddConditionIf(self, conditions=[]):
        self.__condition_if.extend(conditions)

    def _AddConditionUnless(self, conditions=[]):
        self.__condition_unless.extend(conditions)

    # internal functions properties
    @property
    def _Passed(self):
        '''Test all the conditions to see if they all pass
        return True if we have a failure and should skip
        '''
        # loop on skipunless
        for cond in self.__condition_unless:
            if not cond:
                # we had a failure
                self.__reason = cond.Message
                return False
        # loop on skipif
        for cond in self.__condition_if:
            if cond:
                # we had a failure
                self.__reason = cond.NegitiveMessage
                return False

        return True

    @property
    def _Reason(self):
        return self.__reason

    # internal functions
    def _Empty(self):
        '''Removes all condtions tests that have been defined'''
        self.__conditions = []

from __future__ import absolute_import, division, print_function
import autest.testers as testers
from collections import namedtuple
from autest.common.constructor import call_base, smart_init

# hold a set of testers being mapped to a given event to be bound


@smart_init
class TesterSet(object):
    '''
    hold the set of items to be bound for a given named object
    '''
    @call_base()
    def __init__(self, default_tester, testvalue, event, converter=None, kill_on_failure=False, description_group=None, description=None,):
        self._event = event
        self._kill_on_failure = kill_on_failure
        self._description = description
        self._description_grp = description_group
        self._default_tester = default_tester
        self._testvalue = testvalue
        if converter is None:
            self._converter = lambda x: x
        else:
            self._converter = converter

        self._testers = []

    def _create_tester(self, value):
        if isinstance(value, testers._Container):
            value._verify(self._create_tester)
        elif not isinstance(value, testers.Tester):
            # create a tester object
            value = self._default_tester(
                self._converter(value), self._testvalue)
        tester = value
        # set tester with data so it can bind to the correct data
        tester.TestValue = self._testvalue
        if tester.DescriptionGroup is None:
            tester.DescriptionGroup = self._description_grp
        if self._description is not None:
            tester.Description = self._description.format(tester)
        if self._kill_on_failure:
            tester.KillOnFailure = self._kill_on_failure
        return tester

    def assign(self, value):
        self._testers = [self._create_tester(value)]
        return self

    def add(self, value):
        self._testers += [self._create_tester(value)]
        return self

    def _bind(self):
        for tester in self._testers:
            self._event += tester

    # operators
    def __iadd__(self, value):
        return self.add(value)

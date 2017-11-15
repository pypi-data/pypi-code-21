# -*- coding: utf-8 -*-
###########################################################################
# Copyright (c), The AiiDA team. All rights reserved.                     #
# This file is part of the AiiDA code.                                    #
#                                                                         #
# The code is hosted on GitHub at https://github.com/aiidateam/aiida_core #
# For further information on the license, see the LICENSE.txt file        #
# For further information please visit http://www.aiida.net               #
###########################################################################
from time import sleep
# from aiida.work.run import submit
from aiida.work.workchain import WorkChain, ToContext

class ParentWorkChain(WorkChain):

    @classmethod
    def define(cls, spec):
        super(ParentWorkChain, cls).define(spec)
        spec.outline(
            cls.step,
            cls.resulta
        )

    def step(self):
        running = self.runner.submit(SubWorkChain)
        self.report('Submitted {}<{}>'.format(SubWorkChain.__name__, running.pid))
        return ToContext(sub=running)

    def resulta(self):
        self.report('ParentWorkChain finished')

class SubWorkChain(WorkChain):

    @classmethod
    def define(cls, spec):
        super(SubWorkChain, cls).define(spec)
        spec.outline(
            cls.step,
            cls.resulta,
            cls.result2,
            cls.step2,
            cls.result3
        )

    def step(self):
        running = self.runner.submit(BaseWorkChain)
        self.report('Submitted {}<{}>'.format(BaseWorkChain.__name__, running.pid))
        return ToContext(base=running)

    def resulta(self):
        self.report('SubWorkChain finished')

    def result2(self):
        self.report('SubWorkChain 2')

    def step2(self):
        running = self.runner.submit(BaseWorkChain)
        self.report('Submitted {}<{}>'.format(BaseWorkChain.__name__, running.pid))
        return ToContext(base=running)

    def result3(self):
        self.report('SubWorkChain 3')

class BaseWorkChain(WorkChain):

    @classmethod
    def define(cls, spec):
        super(BaseWorkChain, cls).define(spec)
        spec.outline(
            cls.step
        )

    def step(self):
        self.report('huzzah')

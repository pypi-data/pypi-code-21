# -*- coding: utf-8 -*-
###########################################################################
# Copyright (c), The AiiDA team. All rights reserved.                     #
# This file is part of the AiiDA code.                                    #
#                                                                         #
# The code is hosted on GitHub at https://github.com/aiidateam/aiida_core #
# For further information on the license, see the LICENSE.txt file        #
# For further information please visit http://www.aiida.net               #
###########################################################################
from aiida.work.workchain import WorkChain, ToContext

from aiida.orm.data.base import Str, Float

class TestClass(WorkChain):
    """
    Workflow to calculate the force constants and phonon properties using phonopy
    """

    @classmethod
    def define(cls, spec):
        super(TestClass, cls).define(spec)
        spec.input('input_1', valid_type=Float)
        spec.input('input_2', valid_type=Float)

        spec.outline(cls.step1, cls.step2)

    def step1(self):
        print self.inputs.input_1

    def step2(self):
        print self.inputs.input_2
        self.out('result_1', self.inputs.input_1)


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
            cls.resulta
        )

    def step(self):
        running = self.runner.submit(BaseWorkChain)
        self.report('Submitted {}<{}>'.format(BaseWorkChain.__name__, running.pid))
        return ToContext(base=running)

    def resulta(self):
        self.report('SubWorkChain finished')

class BaseWorkChain(WorkChain):

    @classmethod
    def define(cls, spec):
        super(BaseWorkChain, cls).define(spec)
        spec.outline(
            cls.step
        )

    def step(self):
        self.report('BaseWorkChain running')

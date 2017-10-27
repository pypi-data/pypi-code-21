#!/usr/bin/env python
# -*- coding: utf-8 -*-
###########################################################################
# Copyright (c), The AiiDA team. All rights reserved.                     #
# This file is part of the AiiDA code.                                    #
#                                                                         #
# The code is hosted on GitHub at https://github.com/aiidateam/aiida_core #
# For further information on the license, see the LICENSE.txt file        #
# For further information please visit http://www.aiida.net               #
###########################################################################
from aiida.orm.data.base import Str
from aiida.work.run import submit, async
from aiida.work.workchain import WorkChain
from aiida.work.workchain import ToContext


class DummyWorkChain(WorkChain):
    
    @classmethod
    def define(cls, spec):
        super(DummyWorkChain, cls).define(spec)
        spec.input("str_display", valid_type=Str, required=True),
        spec.outline(
            cls.run_sub,
            cls.run_result
        )
        spec.dynamic_output()

    def run_sub(self):
        res = submit(DummySubWorkChain, str_display=Str('subworkchain'))
        return ToContext(sub1=res)

    def run_result(self):
        outdict = {'out_dummy_wc' : Str('result dummy_wc')}
        for link_name, node in outdict.iteritems():
            self.out(link_name, node)


class DummySubWorkChain(WorkChain):
    
    @classmethod
    def define(cls, spec):
        super(DummySubWorkChain, cls).define(spec)
        spec.input("str_display", valid_type=Str, required=True),
        spec.outline(
            cls.run_result
        )
        spec.dynamic_output()

    def run_result(self):
        outdict = {'out_dummy_sub_wc' : Str('result dummy_sub_wc')}
        for link_name, node in outdict.iteritems():
            self.out(link_name, node)
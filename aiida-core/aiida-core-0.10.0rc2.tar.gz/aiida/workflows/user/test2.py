#!/usr/bin/env runaiida
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
from aiida.work.workfunction import workfunction

from aiida.work.run import run, submit
from aiida.orm.data.base import Str, Float, Bool
from aiida.workflows.user.workchain import TestClass


if __name__ == "__main__":

    # Define structure

    import numpy as np


    # This works
    results = run(TestClass,
                  input_1=Float(10),
                  input_2=Float(0)
                  )
    print (results)


    # This is what I want to do and it does not work as I expect
    submit(TestClass,
           input_1=Float(10),
           input_2=Float(0)
           )


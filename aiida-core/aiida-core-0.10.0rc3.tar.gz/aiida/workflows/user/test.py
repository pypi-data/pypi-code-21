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
from aiida.work.run import run
from aiida.workflows.user.workchain import ParentWorkChain
from aiida.work.runner import create_runner, create_daemon_runner
from aiida.work.launch import run_get_pid

runner = create_runner()
# runner = create_daemon_runner()

# runner.run(ParentWorkChain)
result = run_get_pid(ParentWorkChain)
print result
# running = submit(ParentWorkChain)
# print('Submitted {}'.format(running.pid))

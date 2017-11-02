# -*- coding: utf-8 -*-
# :Project:   PatchDB -- Python script execution context
# :Created:   sab 31 mag 2014 12:55:31 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2014, 2016, 2017 Lele Gaifax
#

from __future__ import unicode_literals

import sys
from . import ExecutionContext


class PythonContext(ExecutionContext):
    language_name = 'python'

    execution_context = {'contexts': ExecutionContext.execution_contexts_registry}

    def __init__(self):
        ExecutionContext.__init__(self)
        self.assertions.update({
            'python_3_x': sys.version_info.major == 3,
            'python_2_x': sys.version_info.major == 2,
        })

    def apply(self, patch, options):
        """
        Execute the Python script.

        The script may refers to other `contexts`: in particular
        ``contexts['sql'].connection`` is the open connection to
        the database.
        """

        if options.dry_run:
            ExecutionContext.apply(self, patch, options)
        else:
            local_ns = {'options': options}
            script = self.replaceUserVariables(patch.script)
            if sys.version_info.major >= 3:
                exec(script, self.execution_context, local_ns)
            else:
                exec("exec script in self.execution_context, local_ns")
        self.execution_contexts_registry['sql'].applied(patch, options.dry_run)

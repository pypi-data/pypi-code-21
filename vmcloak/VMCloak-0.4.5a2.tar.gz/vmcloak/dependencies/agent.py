# Copyright (C) 2014-2016 Jurriaan Bremer.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import logging
import os.path

from vmcloak.abstract import Dependency

log = logging.getLogger(__name__)

class Agent(Dependency):
    name = "agent"

    def init(self):
        self.path = None

    def check(self):
        if not self.path or not os.path.exists(self.path):
            log.error("Please provide the path to the new Agent file.")
            return False

    def run(self):
        self.a.upload("C:\\vmcloak\\agent.py", open(self.path, "rb"))

        # Start the Agent in about 10 seconds from now. That should give us
        # enough time to kill the existing Agent.
        self.a.execute("C:\\Python27\\python.exe C:\\vmcloak\\agent.py "
                       "0.0.0.0 %s -s 10000" % self.a.port, async=True)
        self.a.kill()

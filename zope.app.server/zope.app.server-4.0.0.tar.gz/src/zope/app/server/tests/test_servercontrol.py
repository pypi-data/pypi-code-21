import unittest

import zope.app.server.main
from zope.interface.verify import verifyObject
from zope.app.server.servercontrol import serverControl
from zope.applicationcontrol.interfaces import IServerControl


class TestServerControl(unittest.TestCase):

    def tearDown(self):
        zope.app.server.main.exit_status = None

    def test(self):
        verifyObject(IServerControl, serverControl)

    def test_shutdown(self):
        serverControl.shutdown()
        self.assertEqual(zope.app.server.main.exit_status, 0)

    def test_restart(self):
        serverControl.restart()
        self.assertEqual(zope.app.server.main.exit_status, 1)

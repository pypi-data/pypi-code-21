from __future__ import absolute_import, division, print_function
import os
import autest.core.setupitem as setupitem
from autest.core import CopyLogic
from autest.exceptions.setuperror import SetupError
import autest.api as api


class Copy(setupitem.SetupItem):
    def __init__(self, source, target=None, copy_logic=CopyLogic.Default):
        super(Copy, self).__init__(itemname="Copy")
        self.source = source
        self.target = target
        self.copy_logic = copy_logic
        self.Description = "Copy {0} to {1}".format(self.source, self.target)

    def setup(self):
        try:
            self.Copy(self.source, self.target, self.copy_logic)
        except Exception as e:
            raise SetupError('Cannot copy {0} to {1} because:\n {2}'.format(
                self.source, self.target, str(e)))


class FromDirectory(setupitem.SetupItem):
    def __init__(self, source, copy_logic=CopyLogic.Default):
        super(FromDirectory, self).__init__(
            itemname="Setup test from Directory")
        self.source = source
        self.copy_logic = copy_logic
        self.Description = "Copy {0} to sandbox directory".format(self.source)

    def setup(self):
        try:
            self.Copy(self.source, self.SandBoxDir, self.copy_logic)
        except Exception as e:
            raise SetupError('Cannot copy Directory {0} to {1} because:\n {2}'.
                             format(self.source, self.SandBoxDir, str(e)))


class FromTemplate(setupitem.SetupItem):
    def __init__(self, source, copy_logic=CopyLogic.Default):
        super(FromTemplate, self).__init__(itemname="Setup test from Template")
        self.source = source
        self.copy_logic = copy_logic
        self.Description = "Copy {0} to sandbox directory".format(
            os.path.join("templates", self.source))

    def setup(self):
        try:
            src = os.path.join(self.TestRootDir, "templates", self.source)
            dest = self.SandBoxDir
            self.Copy(src, dest, self.copy_logic)
        except Exception as e:
            raise SetupError('Cannot copy {0} to {1} because:\n {2}'.format(
                src, dest, str(e)))


api.AddSetupItem(Copy, "__call__", ns='Copy')
api.AddSetupItem(FromDirectory, ns='Copy')
api.AddSetupItem(FromTemplate, ns='Copy')

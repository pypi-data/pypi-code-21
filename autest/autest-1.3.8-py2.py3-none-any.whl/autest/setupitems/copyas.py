from __future__ import absolute_import, division, print_function
import autest.core.setupitem as setupitem
from autest.exceptions.setuperror import SetupError
import autest.api as api


class CopyAs(setupitem.SetupItem):
    def __init__(self, source, targetdir, targetname=None):
        super(CopyAs, self).__init__(itemname="CopyAs")
        self.source = source
        self.targetdir = targetdir
        self.targetname = targetname
        if targetname:
            self.Description = "Copy {0} to {1} as {2}".format(
                self.source, self.targetdir, self.targetname)
        else:
            self.Description = "Copy {0} to {1}".format(self.source,
                                                        self.targetdir)

    def setup(self):
        try:
            self.CopyAs(self.source, self.targetdir, self.targetname)
        except Exception as e:
            raise SetupError(
                'Cannot copy {0} to {1} as {2} because:\n {3}'.format(
                    self.source, self.targetdir, self.targetname, str(e)))


api.AddSetupItem(CopyAs, "__call__", ns='CopyAs')

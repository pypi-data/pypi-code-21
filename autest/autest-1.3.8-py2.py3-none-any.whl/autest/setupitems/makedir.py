import autest.core.setupitem as setupitem
import autest.api as api


class MakeDir(setupitem.SetupItem):
    def __init__(self, path, mode=None):
        super(MakeDir, self).__init__(itemname="MakeDir")
        self.path = path
        self.mode = mode
        self.Description = "Making Directory {0}".format(self.path)

    def setup(self):
        self.MakeDir(self.path, self.mode)


api.AddSetupItem(MakeDir, "__call__", ns='MakeDir')

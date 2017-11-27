import autest.core.setupitem as setupitem
import autest.api as api


class Chown(setupitem.SetupItem):
    def __init__(self, path, uid, gid, ignore=False):
        super(Chown, self).__init__(itemname="Chown")
        self.path = path
        self.uid = uid
        self.gid = gid
        self.Description = "On {0} with uid: {1} gid: {2}".format(
            self.path, self.uid, self.gid)
        self.ignore = ignore

    def setup(self):
        try:
            self.Chown(self.path, self.uid, self.gid)
        except:
            if not self.ignore:
                raise


api.AddSetupItem(Chown, "__call__", ns='Chown')

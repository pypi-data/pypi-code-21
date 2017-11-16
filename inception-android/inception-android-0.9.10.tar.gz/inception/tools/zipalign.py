from .execwrapper import ExecWrapper
class ZipAlign(ExecWrapper):
    def __init__(self, zipAlignBin):
        super(ZipAlign, self).__init__(zipAlignBin)

    def align(self, src, dest):
        self.clearArgs()
        self.addPreArg("-f")
        self.setArg("v", "4")
        self.addPostArg(src)
        self.addPostArg(dest)

        self.run()
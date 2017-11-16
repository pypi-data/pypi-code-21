from .execwrapper import ExecWrapper
class SignFile(ExecWrapper):
    def __init__(self, signFilePath):
        super(SignFile, self).__init__("perl")
        self.signFilePath = signFilePath
        # self.priv = priv
        # self.pub = pub
        # self.hash = hash
        # self.file = file
        # self.setLongArgPrefix("-")

    def sign(self, priv, pub, hash, f):
        self.clearArgs()
        self.addPreArg(self.signFilePath)
        self.setArg("v", hash)
        self.addPostArg(priv)
        self.addPostArg(pub)
        self.addPostArg(f)
        self.run()
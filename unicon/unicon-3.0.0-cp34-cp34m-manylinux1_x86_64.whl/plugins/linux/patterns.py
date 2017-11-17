from unicon.patterns import UniconCorePatterns

class LinuxPatterns(UniconCorePatterns):
    def __init__(self):
        super().__init__()
        self.continue_connect = r'Are you sure you want to continue connecting \(yes/no\)'
        self.prompt = r'\n(.*([>\$~%]|[^#\s]#))\s?$'


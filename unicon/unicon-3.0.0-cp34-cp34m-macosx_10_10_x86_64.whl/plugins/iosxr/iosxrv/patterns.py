from unicon.plugins.iosxr.patterns import IOSXRPatterns

class IOSXRVPatterns(IOSXRPatterns):
    def __init__(self):
        super().__init__()
        self.enable_prompt = \
            r'^.*?RP/\d+/\d+/CPU\d+:(ios|%N)\s*#'
        self.config_prompt = \
            r'^.*?RP/\d+/\d+/CPU\d+:(ios|%N)\s*\(config.*\)\s*#'



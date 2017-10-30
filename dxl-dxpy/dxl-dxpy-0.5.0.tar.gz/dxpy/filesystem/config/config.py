from collections import UserDict


class Config(UserDict):
    version = 0.1

    def __init__(self, restful_name='fs'):
        from fs.osfs import OSFS
        super(__class__, self).__init__()
        self.restful_name = restful_name
        self.default_fs = OSFS


c = Config()

from cuber import cube
from cuber import utils

class CubeIdle(cube.Cube):
    immutable_args = True
    restorable = False

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def name(self):
        return 'idle_{}'.format(utils.universal_hash(self.kwargs))

    def eval(self):
        return self.kwargs

from . import np
from procgraph import Block, ETERNITY
import warnings


__all__ = ['Solid', 'solid']


class Solid(Block):
    Block.alias('solid')
    Block.output('rgb')
    Block.config('width')
    Block.config('height')
    Block.config('color', default=[1, 1, 1])

    def init(self):
        self.info('init')
        
    def update(self):
        rgb = solid(self.config.width, self.config.height, self.config.color)
        self.info('updating solid ts : %s' % ETERNITY)
        # self.set_output(0, rgb, timestamp=ETERNITY)
        warnings.warn('Eternity is not respected')
        self.set_output(0, rgb, timestamp=0)


def solid(width, height, color):
    rgb = np.zeros((height, width, 3), dtype='uint8')
    for i in range(3):
        rgb[:, :, i] = color[i] * 255
    return rgb


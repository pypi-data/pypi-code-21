import numpy as np
from procgraph import Block
from procgraph.core.registrar_other import simple_block

__all__ = ['TransparentImageAverage']


class ChannelAverage:
    def __init__(self):
        self.value = None
        self.alpha = None

    def update(self, value, alpha):
        if self.value is None:
            self.value = value
            self.alpha = alpha
        else:
            alpha_sum = self.alpha + alpha
            alpha_sum[alpha_sum == 0] = 1
            self.value = (self.value * self.alpha + value * alpha) / alpha_sum
            self.alpha = (self.alpha + alpha)

    def get_value(self):
        return self.value 

    def get_alpha_255(self):
        return self.alpha * 255.0 / self.alpha.max()


class TransparentImageAverage:
    """ Averages images, assuming that alpha means a weight factor. """
    def __init__(self):
        self.channels = [ChannelAverage() for _ in range(3)]

    def update(self, rgba):
        rgb = rgba[:, :, 0:3].astype('float32')
        alpha = rgba[:, :, 3].astype('float32')

        for i in range(3):
            self.channels[i].update(rgb[:, :, i], alpha)

    def get_rgb(self):
        rgbs = np.dstack([self.channels[i].get_value() for i in range(3)])
        rgbs = rgbs.astype('uint8')
        return rgbs

    def get_rgba(self):
        channels = [self.channels[i].get_value().astype('uint8') for i in range(3)]
        channels.append(self.channels[0].get_alpha_255().astype('uint8'))
        
        rgba = np.dstack(channels)
        
        return rgba


# XXX: move away
@simple_block
def to_rgb(rgba):
    return rgba[:, :, 0:3]


class TransparentImageAverageBlock(Block):
    Block.alias('trans_avg')
    Block.input('rgba')
#     Block.output('rgb')
    Block.output('rgba')
    
    def init(self):
        self.tia = TransparentImageAverage()
        
    def update(self):
        self.tia.update(self.input.rgba)
        # self.output.rgb = self.tia.get_rgb()
        self.output.rgba = self.tia.get_rgba()
        

from procgraph import Block
from procgraph.block_utils import check_rgb
from . import np


__all__ = ['Border', 'rgb_pad', 'image_border']


class Border(Block):
    ''' Adds a block around the input image. '''
    Block.alias('border')

    Block.input('rgb', 'Input image.')
    Block.output('rgb', 'Image with borders added around.')
    Block.config('color', 'border color (0-1 rgb)', default=[0, 0, 0])
    Block.config('width', default=1)
    Block.config('left', 'pixel length for left border', default=None)
    Block.config('right', 'pixel length for right border', default=None)
    Block.config('top', 'pixel length for top border', default=None)
    Block.config('bottom', 'pixel length for bottom border', default=None)

    def update(self):
        check_rgb(self, 'rgb')

        def df(x):
            if x is None:
                return self.config.width
            else:
                return x

        # TODO: check color 
        self.output.rgb = image_border(self.input.rgb,
                           left=df(self.config.left),
                           right=df(self.config.right),
                           top=df(self.config.top),
                           bottom=df(self.config.bottom),
                           color=df(self.config.color))

 

def rgb_pad(height, width, color):
    pad = np.zeros((height, width, 3), dtype='uint8')
    for i in range(3):
        pad[:, :, i] = color[i] * 255
    return pad


def image_border(rgb, left=0, right=0, top=0, bottom=0, color=[1, 1, 1]):
    orig_shape = rgb.shape
    
    if left > 0:
        # note: do this every time because it changes throughout
        height, width = rgb.shape[0:2]
        pad = rgb_pad(height, left, color)
        rgb = np.hstack((pad, rgb))

    if right > 0:
        height, width = rgb.shape[0:2]
        pad = rgb_pad(height, right, color)
        rgb = np.hstack((rgb, pad))

    if top > 0:
        height, width = rgb.shape[0:2]
        pad = rgb_pad(top, width, color)
        rgb = np.vstack((pad, rgb))
        assert rgb.shape[0] == height + top

    if bottom > 0:
        height, width = rgb.shape[0:2]
        pad = rgb_pad(bottom, width, color)
        rgb = np.vstack((rgb, pad))
        assert rgb.shape[0] == height + bottom

    assert rgb.shape[0] == orig_shape[0] + top + bottom
    assert rgb.shape[1] == orig_shape[1] + left + right
        
    return rgb



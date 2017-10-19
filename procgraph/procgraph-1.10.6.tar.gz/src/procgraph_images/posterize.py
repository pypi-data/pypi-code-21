from . import np

from procgraph import simple_block
from procgraph.block_utils import assert_rgb_image


@simple_block
def posterize(rgb, levels=2):
    ''' 
        Posterizes the given image with the specified number of levels.
        
        :param rgb: RGB image
        :type rgb: array(HxWx3,uint8),H>0,W>0
    
        :param levels: number of levels
        :type levels: int,>=2
        
        :return: A RGB image with the specified number of levels.
        :rtype: array(HxWx3,uint8)
    '''
    assert_rgb_image(rgb, 'input to rgb2grayscale')

    result = np.zeros(shape=rgb.shape, dtype='uint8')
    for i in range(3):
        channel = rgb[:, :, i].squeeze()
        result[:, :, i] = posterize_channel(channel, levels)

    return result


def posterize_channel(chan, levels):
    ''' 
        Posterizes one channel of an image.
        
        :param rgb: image channel
        :type rgb: array(HxW,uint8),H>0,W>0
    
        :param levels: number of levels
        :type levels: int,>=2
        
        :return: Posterized channel
        :rtype: array(HxW,uint8)
    '''

    assert levels > 1
    # Get the limits
    perc = np.linspace(0, 255.0, levels + 1)
    assert len(perc) == levels + 1

    result = np.zeros(shape=chan.shape, dtype='uint8')
    for level in range(levels):
        lower_bound = perc[level]
        upper_bound = perc[level + 1]
        assert lower_bound < upper_bound
        select = np.logical_and(chan >= lower_bound, chan <= upper_bound)
        target = (lower_bound + upper_bound) * 0.5
        result[select] = target
    return result



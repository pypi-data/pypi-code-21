import numpy as np
from procgraph import COMPULSORY
from procgraph import simple_block

from .pil_conversions import Image_from_array


__all__ = ['resize']

@simple_block
def pil_zoom(value, factor=COMPULSORY):
    """ Zooms by a given factor """
    # TODO: RGBA?
    shape = value.shape[:2]
    shape2 = (int(factor * shape[0]), int(factor * shape[1]))
    height, width = shape2
    image = Image_from_array(value) 
    image = image.resize((width, height))
    result = np.asarray(image.convert("RGB"))
    return result


@simple_block
def resize(value, width=None, height=None):
    ''' 
        Resizes an image.
        
        You should pass at least one of ``width`` or ``height``.
        
        :param value: The image to resize.
        :type value: image
        
        :param width: Target image width.
        :type width: int,>0
        
        :param height: Target image height.
        :type height: int,>0

        :return: image: The image as a numpy array.
        :rtype: rgb
    '''
    H, W = value.shape[:2]


    if width is None and height is None:
        msg = 'You should pass at least one of width or height.'
        raise ValueError(msg)

    if width is None and height is not None:
        width = int((height * 1.0 / H) * W)
    elif height is None and width is not None:
        height = int((width * 1.0 / W) * H)

    if width == W and height == H:
        # print('want: %s have: %s -- No resize necessary' % (value.shape, (width, height)))
        return value.copy()
    
    image = Image_from_array(value)
    # TODO: RGBA?
    image = image.resize((width, height))
    result = np.asarray(image.convert("RGB"))

    assert result.shape[0] == height
    assert result.shape[1] == width
        
    # ratio1 = value.shape[0] * 1.0 / value.shape[1]
    # ratio2 = result.shape[0] * 1.0 / result.shape[1]
    # print('ratio1 : %.2f  result %.2f' % (ratio1, ratio2))

    return result




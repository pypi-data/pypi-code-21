from contracts import contract, describe_value
from procgraph import BadInput, simple_block
from procgraph.block_utils import assert_gray_image, assert_rgb_image
from . import np

@simple_block
def as_uint8(rgb):
    res = rgb.astype('uint8')
    return res

@simple_block
def as_float32(rgb):
    res = rgb.astype('float32')
    return res
    
    
@simple_block
@contract(x='array[HxW](>=0, <=255)', returns='array[HxW](>=0, <=1)')
def range_01_from_255(x):
    """ Divides by 255. """
    return x / 255.0

@simple_block
@contract(returns='array[HxWx3](uint8)')
def torgb(rgb):
    """ Converts all image formats to RGB uint8. """
    
    try:
        # check_convertible_to_rgb(rgb)
        pass
    except ValueError as e:
        raise BadInput(str(e), None, 0)
    
    if rgb.ndim == 2:
        if rgb.dtype == 'float32':
            m = np.amin(rgb)
            M = np.amax(rgb)
            if m < 0 or M > 1:
                msg = 'If float, I assume range [0,1]; found [%s, %s].' % (m, M)
                raise ValueError(msg)
            rgb = (rgb * 255).astype('uint8')
        return gray2rgb(rgb)
    
    nc = rgb.shape[2]
    if nc == 4:
        return rgb[:, :, :3]

    if nc == 3:
        if rgb.dtype == 'float32':
            return (rgb * 255).astype('uint8')
        elif rgb.dtype == 'uint8':
            return rgb
        else:
            msg = 'Expected image format: %s' % describe_value(rgb)
            raise ValueError(msg)

@simple_block
@contract
def rgb2gray(rgb):
    ''' Converts a HxWx3 RGB image into a HxW grayscale image 
        by computing the luminance. 
        
        :param rgb: RGB image
        :type rgb: array[HxWx3](uint8),H>0,W>0
        
        :return: A RGB image in shades of gray.
        :rtype: array[HxW](uint8)
    '''
    assert_rgb_image(rgb, 'input to rgb2grayscale')
    r = rgb[:, :, 0].squeeze()
    g = rgb[:, :, 1].squeeze()
    b = rgb[:, :, 2].squeeze()
    # note we keep a uint8
    gray = r * 299.0 / 1000 + g * 587.0 / 1000 + b * 114.0 / 1000
    gray = gray.astype('uint8')

    return gray


@simple_block
@contract
def gray2rgb(gray):
    ''' 
        Converts a H x W grayscale into a H x W x 3 RGB image 
        by replicating the gray channel over R,G,B. 
        
        :param gray: grayscale
        :type  gray: array[HxW](uint8),H>0,W>0
        
        :return: A RGB image in shades of gray.
        :rtype: array[HxWx3](uint8)
    '''
    assert_gray_image(gray, 'input to gray2rgb')

    rgb = np.zeros((gray.shape[0], gray.shape[1], 3), dtype='uint8')
    for i in range(3):
        rgb[:, :, i] = gray
    return rgb


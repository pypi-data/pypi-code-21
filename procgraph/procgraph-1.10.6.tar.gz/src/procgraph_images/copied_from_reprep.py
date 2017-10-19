from . import np


from procgraph import simple_block, COMPULSORY
from procgraph.block_utils import check_2d_array

# TODO: add for pycontracts
# add_contract('color', 'list[3](>=0,<=1)')


@simple_block
def skim_top(a, top_percent=COMPULSORY):
    ''' Cuts off the top percentile of the array.
    
        :param top_percent: How much to cut off (decimal).
         :type top_percent: float,>=0,<90
    '''
    assert top_percent >= 0 and top_percent < 90
    threshold = np.percentile(a.flat, 100 - top_percent)
    return np.minimum(a, threshold)


@simple_block
def skim_top_and_bottom(a, percent=COMPULSORY):
    ''' Cuts off the top and bottom percentile of the array. 
    
        :param a: Any numpy array. 
         :type a: array[x]
            
        :param percent: How much to cut off (decimal).
         :type percent: float,>=0,<90

        :return: Skimmed version of ``a``.
         :rtype: array[x]
        
    '''
    assert percent >= 0 and percent < 90
    threshold_max = np.percentile(a.flat, 100 - percent)
    threshold_min = np.percentile(a.flat, percent)
    return np.maximum(threshold_min, np.minimum(a, threshold_max))


@simple_block
def posneg(value, max_value=None, skim=0, nan_color=[0.5, 0.5, 0.5], zero_color=[1.0, 1.0, 1.0]):
    """ 
        Converts a 2D float value to a RGB representation, where
        red is positive, blue is negative, white is zero.
    
        :param value: The field to represent.
         :type value: array[HxW]
        
        :param max_value:  Maximum of absolute value (if None, detect).
         :type max_value:  float,>0
        
        :param skim:       Fraction to skim (in percent).
         :type skim:       float,>0,<100
         
        :param nan_color:  Color to give for regions of NaN and Inf.
         :type nan_color:  color
        
        :return: posneg: A RGB image.
         :rtype: array[HxWx3](uint8)

    """

    check_2d_array(value, 'input to posneg')

    # TODO: put this in reprep
    value = value.copy()
    if value.ndim > 2:
        value = value.squeeze()

    if value.dtype == np.dtype('uint8'):
        value = value.astype('float32')

    if len(value.shape) != 2:
        raise Exception('I expected a H x W image, got shape %s.' % 
                        str(value.shape))

    isfinite = np.isfinite(value)
    isnan = np.logical_not(isfinite)
    # set nan to 0
    value[isnan] = 0

    if max_value is None:
        abs_value = abs(value)
        if skim != 0:
            abs_value = skim_top(abs_value, skim)

        max_value = np.max(abs_value)

        if max_value == 0:
            result = np.zeros((value.shape[0], value.shape[1], 3), dtype='uint8')
            for i in range(3):
                result[:, :, i] = zero_color[i] * 255
            return result

    assert np.isfinite(max_value)

    positive = np.minimum(np.maximum(value, 0), max_value) / max_value
    negative = np.maximum(np.minimum(value, 0), -max_value) / -max_value
    positive_part = (positive * 255).astype('uint8')
    negative_part = (negative * 255).astype('uint8')

    result = np.zeros((value.shape[0], value.shape[1], 3), dtype='uint8')

    anysign = np.maximum(positive_part, negative_part)
    R = 255 - negative_part[:, :]
    G = 255 - anysign
    B = 255 - positive_part[:, :]

    # remember the nans
    R[isnan] = nan_color[0] * 255
    G[isnan] = nan_color[1] * 255
    B[isnan] = nan_color[2] * 255

    result[:, :, 0] = R
    result[:, :, 1] = G
    result[:, :, 2] = B

    return result


@simple_block
def scale(value, min_value=None, max_value=None,
                min_color=[1, 1, 1], max_color=[0, 0, 0],
                nan_color=[1, 0, 0]):
    """ 
        Provides a RGB representation of the values by interpolating the range 
        [min(value),max(value)] into the colorspace [min_color, max_color].
        
        :param value: The field to represent.
         :type value: array[HxW],H>0,W>0
            
        :param max_value: If specified, everything *above* is clipped.
         :type max_value: float
        
        :param min_value: If specified, everything *below* is clipped.
         :type min_value: float
    
        :param min_color:  Color to give to the minimum values.
         :type min_color:  color
        :param max_color:  Color to give to the maximum values.
         :type max_color:  color
        :param nan_color:  Color to give for regions of NaN and Inf.
         :type nan_color:  color
        
        :return: scale: A RGB image.
        :rtype: array[HxWx3](uint8)

    """
    # Raises :py:class:`.ValueError` if min_value == max_value

    check_2d_array(value, 'input to scale()')

    # assert_finite(value)
    value = value.copy()
    if value.ndim > 2:
        value = value.squeeze()

    if value.dtype == np.dtype('uint8') or value.dtype == np.dtype('int'):
        value = value.astype('float32')
    # require_shape((gt(0), gt(0)), value)

    min_color = np.array(min_color)
    max_color = np.array(max_color)
    nan_color = np.array(nan_color)
    # require_shape((3,), min_color)
    # require_shape((3,), max_color)

    isnan = np.logical_not(np.isfinite(value))

    if max_value is None:
        value[isnan] = -np.inf
        max_value = np.max(value)

    if min_value is None:
        value[isnan] = np.inf
        min_value = np.min(value)

    if (max_value == min_value
        or np.isnan(min_value)
        or np.isnan(max_value)):
        # XXX: maybe allow set this case as an exception?
#        raise ValueError('I end up with max_value = %s = %s = min_value.' % \
#                         (max_value, min_value))
        result = np.zeros((value.shape[0], value.shape[1], 3), dtype='uint8')
        result[:, :, :] = 255
        return result

    value01 = (value - min_value) / (max_value - min_value)

    # Cut at the thresholds
    value01 = np.maximum(value01, 0)
    value01 = np.minimum(value01, 1)

    result = np.zeros((value.shape[0], value.shape[1], 3), dtype='uint8')

    for u in [0, 1, 2]:
        col = 255 * ((1 - value01) * min_color[u] \
                                 + (value01) * max_color[u])
        col[isnan] = nan_color[u] * 255
        result[:, :, u] = col

    return result

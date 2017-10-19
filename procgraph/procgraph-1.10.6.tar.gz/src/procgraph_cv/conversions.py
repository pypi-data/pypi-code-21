from . import cv
from . import np


def numpy_to_cv(numpy_array):
    ''' Converts a HxW or HxWx3 numpy array to OpenCV 'image' '''
    
    dtype2depth = {
        'uint8': cv.IPL_DEPTH_8U,
        'int8': cv.IPL_DEPTH_8S,
        'uint16': cv.IPL_DEPTH_16U,
        'int16': cv.IPL_DEPTH_16S,
        'int32': cv.IPL_DEPTH_32S,
        'float32': cv.IPL_DEPTH_32F,
        'float64': cv.IPL_DEPTH_64F,
    }

    if len(numpy_array.shape) == 2:
        (height, width) = numpy_array.shape
        nchannels = 1
    elif len(numpy_array.shape) == 3:
        (height, width, nchannels) = numpy_array.shape
    else:
        raise ValueError('Invalid format shape %s' % str(numpy_array.shape))

    im_cv = cv.CreateImage((width, height),
                           dtype2depth[str(numpy_array.dtype)],
                           nchannels)
    cv.SetData(im_cv,
               numpy_array.tostring(),
               numpy_array.dtype.itemsize * width * nchannels)
    return im_cv


def cv_to_numpy(im):
    '''Converts opencv to numpy '''
    depth2dtype = {
        cv.IPL_DEPTH_8U: 'uint8',
        cv.IPL_DEPTH_8S: 'int8',
        cv.IPL_DEPTH_16U: 'uint16',
        cv.IPL_DEPTH_16S: 'int16',
        cv.IPL_DEPTH_32S: 'int32',
        cv.IPL_DEPTH_32F: 'float32',
        cv.IPL_DEPTH_64F: 'float64',
    }

    a = np.fromstring(
         im.tostring(),
         dtype=depth2dtype[im.depth],
         count=im.width * im.height * im.nChannels)
    a.shape = (im.height, im.width, im.nChannels)
    return a


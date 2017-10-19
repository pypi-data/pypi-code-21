
from ..core.exceptions import BadInput
from contracts.interface import describe_value


# TODO: make naming uniform
def check_2d_array(value, name=None):
    import numpy as np

    ''' Checks that we have 2D numpy array '''
    if not isinstance(value, np.ndarray):
        raise BadInput('Expected 2d array, got %s.' % value.__class__.__name__,
                       None, name)

    if len(value.shape) != 2:
        raise BadInput('Expected 2D array, got %s.' % str(value.shape),
                       None, name)


def assert_rgb_image(image, name=None):
    import numpy as np
    if not isinstance(image, np.ndarray):
        raise BadInput('Expected RGB image for %r, got %s.' % 
                       (name, image.__class__.__name__),
                        None, name)

    if image.dtype != 'uint8':
        raise BadInput('Expected RGB image for %r, got an array %s %s.' % 
                            (name, str(image.shape), image.dtype), None, name)

    if len(image.shape) != 3 or image.shape[2] != 3:
        raise BadInput('Bad shape for %s, expected RGB, got %s.' % 
                        (name, str(image.shape)), None, name)


def assert_gray_image(image, name=None):
    import numpy as np
    if not isinstance(image, np.ndarray):
        raise BadInput('Expected a grayscale image for %r, got %s.' % 
                       (name, image.__class__.__name__), None, name)

    if image.dtype != 'uint8':
        raise BadInput('Expected a grayscale image for %r, got an array %s %s.'
                       % 
                            (name, str(image.shape), image.dtype),
                             None, name)

    if len(image.shape) != 2:
        raise BadInput('Bad shape for %r, expected grayscale, got %s.' % 
                        (name, str(image.shape)), None, name)


def check_numpy_array(value):
    import numpy as np
    if not isinstance(value, np.ndarray):
        msg = 'Expected array: %s' % describe_value(value)
        raise ValueError(msg)

def check_convertible_to_rgb(image):
    check_numpy_array(image)
    
    if image.ndim == 3:
        good = image.shape[2] in [3, 4]
        if not good:
            msg = 'Wrong dimensions: %s' % image.shape
            raise ValueError(msg)
        
    if image.ndim > 3 or image.ndim <= 1:
        msg = 'Bad shape: %s' % image.shape
        raise ValueError(msg)
        
    if image.dtype == 'uint8':
        pass
    elif image.dtype == 'float32':   
        imin = image.min()
        imax = image.max() 
        ok = imin >= 0 and imax <= 1
        if not ok:
            msg = 'Invalid values range: %s %s' % (imin, imax)
            raise ValueError(msg)
    else:
        msg = 'invalid dtype %r' % image.dtype
        raise ValueError(msg)
    
def input_check_numpy_array(block, signal):
    try:
        check_numpy_array(block.get_input(signal))
    except ValueError as e:
        raise BadInput(str(e), block, signal)

def input_check_convertible_to_rgb(block, signal): 
    try:
        check_convertible_to_rgb(block.get_input(signal))
    except ValueError as e:
        raise BadInput(str(e), block, signal)
    

def input_check_rgb_or_grayscale(block, input):  # @ReservedAssignment
    ''' Checks that the selected input is either a grayscale or RGB image.
        That is, a numpy array of uint8 either H x W,  H x W x 3,
        or HxWx4. 
        Raises BadInput if it is not. 
    '''
    # TODO: write this better
    
    image = block.get_input(input)
    input_check_numpy_array(block, input)

    if image.dtype != 'uint8':
        msg = ('Expected an image, got an array %s %s.' % 
                (str(image.shape), image.dtype))
        raise BadInput(msg, block, input)
    
    shape = image.shape
    if len(shape) == 3:
        depth = shape[2]
        if not depth in [3, 4]:
            msg = 'Bad shape for image: %s' % str(shape)
            raise BadInput(msg, block, input)
    elif len(shape) == 2:
        pass
    else:
        msg = 'Bad shape for image: %s' % str(shape)
        raise BadInput(msg, block, input)

    if shape[0] == 0 or shape[1] == 0:
        msg = 'Image with zero width or height: %s' % (str(shape))
        raise BadInput(msg, block, input)

def check_rgb(block, input):  # @ReservedAssignment
    ''' Checks that the selected input is either  a RGB image.
        That is, a numpy array of uint8 of shape H x W x 3. 
        Raises BadInput if it is not. 
    '''
    image = block.get_input(input)
    import numpy as np
    if not isinstance(image, np.ndarray):
        raise BadInput('Expected RGB, this is not even a '
            'numpy array: %s' % image.__class__.__name__, block, input)
    if image.dtype != 'uint8':
        raise BadInput('Expected an image, got an array %s %s.' % 
                            (str(image.shape), image.dtype), block, input)
    shape = image.shape
    if len(shape) == 3:
        if shape[2] != 3:
            raise BadInput('Bad shape for image: %s' % str(shape),
                           block, input)
    else:
        raise BadInput('Bad shape for image: %s' % str(shape), block, input)

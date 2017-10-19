import numpy

from procgraph import simple_block


@simple_block
def gradient1d(a):
    ''' 
        Computes the gradient of a 1D array.
    
        :param a: Numpy array
        :type a: array(N),N>3
        
        :return: typed: The gradient of the array. 
        :rtype: array
    '''
    a = numpy.array(a)

    if len(a.shape) != 1 or len(a) < 3:
        raise ValueError('Expected 1D array, got shape %s' % str(a.shape))

    b = numpy.ndarray(shape=a.shape, dtype=a.dtype)

    n = len(a)
    for i in xrange(1, n - 1):
        b[i] = (a[i + 1] - a[i - 1]) / 2

    b[0] = b[1]
    b[-1] = b[-2]

    return b

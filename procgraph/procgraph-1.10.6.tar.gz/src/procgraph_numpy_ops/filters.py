import numpy as np
from numpy import multiply, array

from procgraph import COMPULSORY, register_simple_block, simple_block
from procgraph.core.block import Block


@simple_block
def astype(a, dtype=COMPULSORY):
    ''' 
        Converts an array using the ``astype`` function. 
    
        :param a: Numpy array
        :type a: array
        
        :param dtype: The new dtype.
        :type dtype: string
        
        :return: typed: The Numpy array with the new type. 
        :rtype: array
    '''
    return a.astype(dtype)


@simple_block
def take(a, axis=0, indices=COMPULSORY):
    assert indices != COMPULSORY
    a = np.array(a)
    indices = list(indices)  # parsingresult bug
    axis = int(axis)
    try:
        return a.take(axis=axis, indices=indices).squeeze()
    except Exception as e:
        raise Exception('take(axis=%s,indices=%s) failed on array '
                        'with shape %s: %s' % (axis, indices, a.shape, e))

@simple_block
def sub(a, f=COMPULSORY):
    """ Takes a field """
    return a[f]


@simple_block
def outer(a, b):
    ''' 
        Outer product of two vectors.
    
        This is a wrapper around :py:func:`np.multiply.outer`.
        
        :param a: First vector.
        :param b: Second vector.
        :return: outer: Outer product of the two vectors. 
    '''
    a = array(a)
    b = array(b)
    res = multiply.outer(a, b)
    return res


@simple_block
def select(x, every=COMPULSORY):
    '''
        Selects some of the elements of ``x``.
        
        :param x: Numpy array that can be flatly addressed.
        :param every: How many to jump (every=2 takes only the even elements).
        :return: decimated: The decimated output.
    '''
    assert every != COMPULSORY
    n = len(x)
    return x[range(0, n, every)]


@simple_block
def normalize_Linf(x):
    ''' Normalize a vector such that ``|x|_inf = max(abs(x))= 1``. 
    
        :param x: Any numpy array.
        :return: normalized: The same array normalized.
         
    '''
    return x / np.abs(x).max()



@simple_block
def minimum(value, threshold=COMPULSORY):
    ''' Limits the numpy array to the given threshold. 
    
        :param value: Any numpy array.
        :return: Array of same shape.
    '''
    assert threshold != COMPULSORY
    return np.minimum(value, threshold)


@simple_block
def maximum(value, threshold=COMPULSORY):
    ''' Limits the numpy array to the given threshold. '''
    assert threshold != COMPULSORY
    return np.maximum(value, threshold)


@simple_block
def norm(value, ord=None):  # @ReservedAssignment
    ''' Returns the norm of the vector. 
    
        ord=None  Frobenius for matrix    2-norm for vectors
        2         2-norm (largest sing.value)    
    '''
    return np.linalg.norm(value, ord)


@simple_block
def norm2(value):  # @ReservedAssignment
    ''' Returns the norm of the vector. '''
    return np.linalg.norm(value)

# XXX: not sure the best thing to do
@simple_block
def array(value):
    ''' Converts the value to a Numpy array. '''
    return np.array(value)

@simple_block
def list2array(value):
    """ Converts a list of uniform elements to a Numpy array. """
    return np.array(value, dtype=value[0].dtype)

register_simple_block(np.mean, 'mean', params={'axis': 0},
      doc='Wrapper around :np:data:`np.mean`.')

register_simple_block(np.square, 'square',
      doc='Wrapper around :np:data:`np.square`.')

register_simple_block(np.log, 'log',
      doc='Wrapper around :np:data:`np.log`.')

register_simple_block(np.abs, 'abs',
      doc='Wrapper around :np:data:`np.absolute`.')

register_simple_block(np.sign, 'sign',
      doc='Wrapper around :np:data:`np.sign`.')

register_simple_block(np.arctan, 'arctan',
      doc='Wrapper around :np:data:`np.arctan`.')

register_simple_block(np.real, 'real',
      doc='Wrapper around :np:data:`np.real`.')


register_simple_block(lambda x, y: np.dstack((x, y)), 'dstack',
                      num_inputs=2,
      doc='Wrapper around :np:data:`np.ma.dstack`.')

register_simple_block(lambda x, y: np.hstack((x, y)), 'hstack',
                      num_inputs=2,
      doc='Wrapper around :np:data:`np.ma.hstack`.')

register_simple_block(lambda x, y: np.vstack((x, y)), 'vstack',
                      num_inputs=2,
      doc='Wrapper around :np:data:`np.ma.vstack`.')

register_simple_block(lambda x: np.max(array(x).flat), 'max',
      doc='Maximum over **all** elements. ')

register_simple_block(lambda x: np.sum(array(x).flat), 'sum',
      doc='Sum over **all** elements. ')

register_simple_block(np.sum, 'sum_axis',
      doc='Sum over the axis. ')


register_simple_block(np.flipud, 'flipud',
     doc='Flips the array up/down (wrapper for :py:func:`np.flipud`.)')

register_simple_block(np.fliplr, 'fliplr',
     doc='Flips the array left/right (wrapper for :py:func:`np.fliplr`.)')

register_simple_block(np.transpose, 'transpose',
     doc='Tranpose (wrapper for :py:func:`np.transpose`.)')


register_simple_block(np.radians, 'deg2rad',
    doc='Converts degrees to radians (wrapper around '
        ':np:data:`np.radians`.)')

register_simple_block(np.degrees, 'rad2deg',
    doc='Converts radians to degrees (wrapper around '
        ':np:data:`np.degrees`.)')



class HSplit(Block):
    ''' Splits an array along the first axis. '''

    Block.alias('hsplit')

    Block.input('value')

    Block.output('half1')
    Block.output('half2')

    def update(self):
        value = self.input.value
        h = value.shape[0] / 2
        self.output.half1 = value[0:h, ...]
        self.output.half2 = value[h:, ...]

 

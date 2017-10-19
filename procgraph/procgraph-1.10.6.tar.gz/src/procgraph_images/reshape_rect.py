from procgraph import simple_block
from . import np

__all__ = ['reshape_rectangular']


@simple_block
def reshape_rectangular(x, tall=True):
    ''' 
        If x is not 2D already, reshape it to 2D using the best
        factorization.    
        
        By default, the output is a "tall" array.
        
        Note that if the size of x is a prime number N,
        the output will be 1 x N.
    '''
    if x.ndim == 2:
        return x

    shape = get_best_shape(x.size, tall=tall)
    x = x.reshape(shape)
    return x


def get_best_shape(size, tall=True):
    # Find all divisors
    divs = list(divisors(size))

    # Order this by similarity
    def score(x):
        """ 0 if square, positive if skewed. """
        a, b = x
        return np.abs(np.log(a) - np.log(b))

    divso = sorted(divs, key=score)

    # print('divisors: %s' % divso)
    shape = divso[0]

    it_is_tall = shape[0] > shape[1]
    transpose = tall ^ it_is_tall
    if transpose:
        shape = (shape[1], shape[0])

    return shape


def divisors(size):
    ''' 
        Returns a list of (a, b) tuples such that a*b=c and a<=b.
        
        (a very naive implementation) 
    '''
    L = []
    for i in range(1, size + 1):
        if size % i == 0:
            a, b = i, size / i
            L.append((min(a, b), max(a, b)))
    return list(set(L))


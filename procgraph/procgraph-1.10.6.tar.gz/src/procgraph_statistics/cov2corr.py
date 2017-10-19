
from procgraph import simple_block


@simple_block
def cov2corr(covariance, zero_diagonal=True):
    ''' 
    Compute the correlation matrix from the covariance matrix.
    If zero_diagonal = True, the diagonal is set to 0 instead of 1. 

    :param zero_diagonal: Whether to set the (noninformative) diagonal to zero.
    :param covariance: A 2D numpy array.
    :return: correlation: The exctracted correlation.
    
    '''
    from numpy import multiply, sqrt

    # TODO: add checks
    outer = multiply.outer

    sigma = sqrt(covariance.diagonal())
    M = outer(sigma, sigma)
    correlation = covariance / M

    if zero_diagonal:
        for i in range(covariance.shape[0]):
            correlation[i, i] = 0

    return correlation


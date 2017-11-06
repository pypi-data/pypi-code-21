from __future__ import print_function

import math
import scipy.stats


class DistributionValue(object):

    def __init__(self):
        self.value = None

    def sample(self):
        raise NotImplementedError('Abstract method')

    def __float__(self):
        return self.sample()

    def __lt__(self, other):
        raise NotImplementedError('Abstract method')

    def __le__(self, other):
        return self.__lt__(other)

    def __eq__(self, other):
        raise NotImplementedError('Abstract method')

    def __gt__(self, other):
        return 1.0 - self.__le__(other)

    def __ge__(self, other):
        return 1.0 - self.__lt__(other)

    def constrain(self, low=None, high=None):
        """Truncate the distribution.

        :param low: lower bound (can be None)
        :param high: higher bound (can be None)
        """
        raise NotImplementedError('Abstract method')


class ScipyCDV(DistributionValue):

    def __init__(self, scipy_dist, loc=0.0, scale=1.0):
        DistributionValue.__init__(self)
        self.loc = loc
        self.scale = scale

        self.scipy_dist = scipy_dist

    def sample(self):
        return self.scipy_dist.rvs(self.loc, self.scale)

    def __lt__(self, other):
        if isinstance(other, ScipyCDV):
            other_cdf = other.scipy_dist.cdf
        else:
            other_cdf = lambda x: float(x < other)

        return self.scipy_dist.expect(other_cdf, ((), self.loc, self.scale))

    def plot(self, d=1e-5):
        import matplotlib.pyplot as plt
        import numpy

        x = numpy.linspace(self.scipy_dist.ppf(d, self.loc, self.scale),
                           self.scipy_dist.ppf(1 - d, self.loc, self.scale), 100)
        return plt.plot(x, self.scipy_dist.pdf(x, self.loc, self.scale))

    def __add__(self, other):
        if isinstance(other, DistributionValue):
            raise TypeError('sum of distributions not supported')
        else:
            return self.__class__(self.loc + other, self.scale)

    def __sub__(self, other):
        if isinstance(other, DistributionValue):
            raise TypeError('subtract of distributions not supported')
        else:
            return self.__class__(self.loc - other, self.scale)

    def __mul__(self, other):
        if isinstance(other, DistributionValue):
            raise TypeError('product of distributions not supported')
        else:
            return self.__class__(self.loc * other, self.scale * other)

    def __div__(self, other):
        if isinstance(other, DistributionValue):
            raise TypeError('product of distributions not supported')
        else:
            return self.__class__(self.loc / other, self.scale / other)


class NormalDistValue(ScipyCDV):

    def __init__(self, *args):
        ScipyCDV.__init__(self, scipy.stats.norm, *args)

    def __add__(self, other):
        if isinstance(other, NormalDistValue):
            # Sum of gaussians is gaussian.
            return self.__class__(self.loc + other.loc,
                                  math.sqrt(math.pow(self.scale, 2) + math.pow(other.scale, 2)))
        else:
            return ScipyCDV.__add__(other)

    def __sub__(self, other):
        if isinstance(other, NormalDistValue):
            # Difference of gaussians is gaussian.
            return self.__class__(self.loc - other.loc,
                                  math.sqrt(math.pow(self.scale, 2) + math.pow(other.scale, 2)))
        else:
            return ScipyCDV.__sub__(other)

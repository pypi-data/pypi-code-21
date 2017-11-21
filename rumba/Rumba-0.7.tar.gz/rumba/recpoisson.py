#
# A library to manage ARCFIRE experiments
#
#    Copyright (C) 2017 Nextworks S.r.l.
#    Copyright (C) 2017 imec
#
#    Sander Vrijders   <sander.vrijders@ugent.be>
#    Dimitri Staessens <dimitri.staessens@ugent.be>
#    Vincenzo Maffione <v.maffione@nextworks.it>
#    Marco Capitani    <m.capitani@nextworks.it>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., http://www.fsf.org/about/contact/.
#

import math
import random

import sys

if sys.version_info < (3, 2):
    from repoze.lru import lru_cache
    # from functools32 import lru_cache
else:
    from functools import lru_cache


@lru_cache(1000)
def _get_poisson_var(parameter):
    return Poisson(parameter)


class Poisson(object):

    def __init__(self, parameter):
        self.parameter = parameter

        def c_p(k):
            """Compute the Poisson CDF for k iteratively."""
            if k == 0:
                return self._p(0)
            else:
                return self._compute_poisson_cdf(k - 1) + self._p(k)
        self._compute_poisson_cdf = lru_cache(int(2.5*self.parameter) + 1)(c_p)

    @staticmethod
    def _get_random():
        return random.random()

    def _p(self, k):
        # l^k * e^-l / k!
        # Computed as exp(klog(l) - l - log(k!))
        l = self.parameter
        l_to_the_k = k * math.log(l)
        k_fact = sum([math.log(i + 1) for i in range(k)])
        return math.exp(l_to_the_k - l - k_fact)

    def sample(self):
        # The idea is:
        # take a sample from U(0,1) and call it f.
        # Let x be s.t. x = min_N F(x) > f
        # where F is the cumulative distribution function of Poisson(parameter)
        # return x
        f = self._get_random()

        # We compute x iteratively by computing
        # \sum_k(P=k)
        # where P ~ Poisson(parameter) and stopping as soon as
        # it is greater than f.
        # We use the cache to store results.
        current_cdf = -1
        current_x = -1
        while current_cdf < f:
            current_x += 1
            current_cdf = self._compute_poisson_cdf(current_x)
        return current_x


def poisson(parameter):
    return _get_poisson_var(parameter).sample()

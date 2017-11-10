# -*- coding: utf-8 -*-
"""
sun_combinatorics module
----------------------

utilities for combinatorics involved with SU(N) operators

:author: Alexander Wietek
"""

import numpy as np
import scipy.special

def dim_sun_rep(N, nc):
    """
    return dimension of SU(N) representation, single-row with nc columns
    """
    return int(scipy.special.binom(N + nc - 1, nc))

def get_nth_pattern(nboxes, nballs, num):
    """
    n-th pattern of nballs distributed amongst nboxes
    """
    state = 0
    counter = num
    for n_varying_bits in range(nballs-1, -1, -1):
        n_combinations = 0
	for n_allowed_pos in range(n_varying_bits, nboxes + 1, 1):
	    n_combinations += scipy.special.binom(n_allowed_pos,n_varying_bits);
	    if n_combinations > counter:
		counter -= n_combinations -\
	                   scipy.special.binom(n_allowed_pos,n_varying_bits);
		state |= (1 << n_allowed_pos);
		break
    return state


def get_n_for_pattern(nboxes, nballs, pattern):
    """
    index n of pattern of nballs distributed amongst nboxes
    """
    n=0
    workpattern = int(pattern)
    for n_varying_bits in range(nballs-1, -1, -1):
        for i in range(0, nboxes+1, 1):
            # MSB is at 2^i
            if ((1 << (i+1)) > workpattern):
                n += int(scipy.special.binom(i,n_varying_bits+1))
        	workpattern ^= 1 << i
        	break
    return n


def gbit(number, nbit):
    return (number >> nbit) & 1

# function for enumerating all multisets
def get_nth_multiset(nboxes, nballs, num):
    multiset = np.zeros(nboxes, dtype=int)
    stars_and_bars = get_nth_pattern(nboxes + nballs - 1, nballs, num)
    current_star = 0
    for current_star_or_bar in range(nboxes + nballs - 1):
        if gbit(stars_and_bars, current_star_or_bar) == 0:
            current_star += 1
        else:
            multiset[current_star] += 1
    return multiset


def get_n_for_multiset(nboxes, nballs, multiset):
    stars_and_bars = 0
    current_star_or_bar=0
    for current_star in range(len(multiset)):
        for i in range(multiset[current_star]):
            stars_and_bars |= 1 << current_star_or_bar
            current_star_or_bar += 1
        current_star_or_bar += 1
    return get_n_for_pattern(nboxes + nballs - 1, nballs, stars_and_bars)

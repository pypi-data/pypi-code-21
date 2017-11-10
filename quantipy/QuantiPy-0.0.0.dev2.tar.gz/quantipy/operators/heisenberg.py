# -*- coding: utf-8 -*-
"""
Heisenberg module
=================

module to create heisenberg operator matrices for arbitrary spin or SU(N) generalizations

:author: Alexander Wietek
"""
import numpy as np
import scipy
from quantipy.utils.sun_combinatorics import dim_sun_rep, get_nth_multiset, get_n_for_multiset


__all__ = ["heisenberg_bond", "spin_matrices", "heisenberg_bond_sun",
           "heisenberg_bond_sun_antiferro", "sun_generator_matrix",
           "sun_generator_matrix_conj"]


def heisenberg_bond(spin=2):
    """
    Creates the Heisenberg bond (SU(2) algebra)
    
    .. math::
        S_i \cdot S_j

    for specified value of the spin 

    :param spin: spin S for SU(2) generators **Optional**. Default: 2
    :type spin: int
    :return: bond matrix of Heisenberg bond
    :rtype: numpy.ndarray
    """
    if spin < 2:
        raise ValueError("Invalid Value for spin")
    sx,sy,sz = spin_matrices(spin)
    heis = np.kron(sx, sx) + np.kron(sy, sy) + np.kron(sz, sz)
    return np.real(heis)


def spin_matrices(spin=2):
    """
    Creates the spin matrices (SU(2) algebra)
    
    .. math::
        S^x, S^y, S^z 

    for specified value of the spin 

    :param spin: spin S for SU(2) generators **Optional**. Default: 2
    :type spin: int
    :return: tuple containing spin matrices
    :rtype: tuple of numpy.ndarrays
    """
    if spin < 2:
        raise ValueError("Invalid Value for spin")
    S = (float(spin) - 1.0)/2

    S_p = np.zeros((spin, spin))
    S_m = np.zeros((spin, spin))
    S_z = np.zeros((spin, spin))
    
    for i in range(spin-1):
        m = i-S;
        S_p[i, i+1] = np.sqrt(float( (S*(S+1) - m*(m+1))))
        S_m[i+1, i] = np.sqrt(float( (S*(S+1) - m*(m+1))))
        
    S_x = (S_p + S_m)/2.
    S_y = (S_p - S_m)/(2.*1j)
    for i in range(spin):
        m = S - i;
        S_z[i,i] = float(m)
    return S_x, S_y, S_z


def heisenberg_bond_sun(N, k=1):
    """
    Creates the Heisenberg bond (SU(N) algebra)
    
    .. math::
        \sum\limits_{m,n} S_i^{mn} S_j^{nm}

    for specified value of N and number of columns in single-row Young-Tableaux  

    :param N: N for SU(N)
    :type N: int
    :param k: number of columns in single-row Young-Tableaux **Optional**. Default: 1
    :type k: int
    :return: bond matrix of SU(N) Heisenberg bond
    :rtype: numpy.ndarray
    """
    if N < 2:
        raise ValueError("Invalid Value for N in SU(N)")
    if k < 1:
        raise ValueError("Invalid Value for k")
    
    localdim = dim_sun_rep(N,k)
    localdimsq = localdim**2
    bondmatrix = np.zeros((localdimsq, localdimsq))
    for i in range(localdim):
        for j in range(localdim):
            idx = _index(i,j,localdim)
            
            # Apply SU(N) k column generators
            state1 = get_nth_multiset(N,k,i)
            state2 = get_nth_multiset(N,k,j)
            # print i,j,state1, state2
            
            for m in range(N):
                for n in range(N):
                    coeff1, newstate1 = _apply_generator(m, n, state1)
                    coeff2, newstate2 = _apply_generator(n, m, state2)
                    # print  m,n, state1, state2, "->" , newstate1, newstate2, coeff1,coeff2

                    if np.abs(coeff1*coeff2)>1e-10:
                        new_i = get_n_for_multiset(N, k, newstate1)
                        new_j = get_n_for_multiset(N, k, newstate2)
                        new_idx = _index(new_i, new_j, localdim)
                        # print  state1, state2, m,n, newstate1, newstate2, coeff1*coeff2, idx, new_idx

                        bondmatrix[idx, new_idx] += -coeff1*coeff2
    return (bondmatrix + np.eye(localdimsq)*k**2/float(N))/float(N)


def heisenberg_bond_sun_antiferro(N, k):
    """
    Creates the antiferromagnetic Heisenberg bond (SU(N) algebra)
    
    .. math::
        \sum\limits_{m,n}S_i^{mn} S_j^{nm}

    for specified value of N and number of columns in single-row Young-Tableaux.
    On the second site the conjugate representation of SU(N) is chosen.

    :param N: N for SU(N)
    :type N: int
    :param k: number of columns in single-row Young-Tableaux **Optional**. Default: 1
    :type k: int
    :return: bond matrix of antiferromagnetic SU(N) Heisenberg bond
    :rtype: numpy.ndarray
    """
    localdim = dim_sun_rep(N,k)
    localdimsq = localdim**2
    bondmatrix = np.zeros((localdimsq, localdimsq))
    for i in range(localdim):
        for j in range(localdim):
            idx = _index(i,j,localdim)
            
            # Apply SU(N) k column generators
            state1 = get_nth_multiset(N,k,i)
            state2 = get_nth_multiset(N,k,j)
            # print i,j,state1, state2
            
            for m in range(N):
                for n in range(N):
                    coeff1, newstate1 = _apply_generator(m, n, state1)
                    coeff2, newstate2 = _apply_generator_conj(n, m, state2)
                    # print  m,n, state1, state2, "->" , newstate1, newstate2, coeff1,coeff2

                    if np.abs(coeff1*coeff2)>1e-10:
                        new_i = get_n_for_multiset(N, k, newstate1)
                        new_j = get_n_for_multiset(N, k, newstate2)
                        new_idx = _index(new_i, new_j, localdim)
                        # print  state1, state2, m,n, newstate1, newstate2, coeff1*coeff2, idx, new_idx

                        bondmatrix[idx, new_idx] += -coeff1*coeff2
    return (bondmatrix + np.eye(localdimsq)*k**2/float(N))/float(N)


def sun_generator_matrix(N, k, m, n):
    """
    Creates the SU(N) generator matrix
    
    .. math::
       S^{mn}

    :param N: N for SU(N)
    :type N: int
    :param k: number of columns in single-row Young-Tableaux
    :type k: int
    :param m: index m of generator
    :type m: int
    :param n: index n of generator
    :type n: int
    :return: generator S^{mn} of SU(N) algebra
    :rtype: numpy.ndarray
    """
    localdim = dim_sun_rep(N,k)
    smn=np.zeros((localdim, localdim))
    for i in range(localdim):
        state = get_nth_multiset(N,k,i)
        coeff, newstate = _apply_generator(m, n, state)
        new_i = get_n_for_multiset(N, k, newstate)
        smn[i, new_i] += coeff
    return smn


def sun_generator_matrix_conj(N,k,m,n):
    """
    Creates the SU(N) generator matrix
    
    .. math::
       S^{mn}

    in conjugate representation

    :param N: N for SU(N)
    :type N: int
    :param k: number of columns in single-row Young-Tableaux
    :type k: int
    :param m: index m of generator
    :type m: int
    :param n: index n of generator
    :type n: int
    :return: generator S^{mn} of SU(N) algebra
    :rtype: numpy.ndarray
    """
    localdim = dim_sun_rep(N,k)
    smn=np.zeros((localdim, localdim))
    for i in range(localdim):
        state = get_nth_multiset(N,k,i)
        coeff, newstate = _apply_generator_conj(m, n, state)
        new_i = get_n_for_multiset(N, k, newstate)
        smn[i, new_i] += coeff
    return smn


def _apply_generator(m,n,multiset):
    """
    applies the generator m+ n- to multiset
    """
    if multiset[n] == 0:
        return 0., np.zeros_like(multiset)
    else:
        new_multiset = np.copy(multiset)
        if m != n:
            coeff = np.sqrt(float((multiset[m]+1)*multiset[n]))
        else:
            coeff = float(multiset[m])
        new_multiset[m] += 1
        new_multiset[n] -= 1
        return coeff, new_multiset


def _apply_generator_conj(m,n,multiset):
    """
    applies the generator m- n+ to multiset
    """
    if multiset[m] == 0:
        return 0., np.zeros_like(multiset)
    else:
        new_multiset = np.copy(multiset)
        if m != n:
            coeff = np.sqrt(float(multiset[m]*(multiset[n]+1)))
        else:
            coeff = float(multiset[m])
        new_multiset[n] += 1
        new_multiset[m] -= 1
        return coeff, new_multiset

    
def _index(i,j,dim):
    """
    get index in bondmatrix
    """
    return i*dim + j

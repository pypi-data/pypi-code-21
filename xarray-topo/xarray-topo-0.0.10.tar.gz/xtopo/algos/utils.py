"""
Implementation of some base algorithms used internally in this package.

"""
import numpy as np
import numba


@numba.njit
def solve_tdma(a, b, c, r, n):
    """Solve a tri-diagonal system of equations using the Tri-diagonal
    matrix algorithm (TDMA, or Thomas' algorithm).

    Inputs:
    `a` is lower diagonal, `b` is diagonal, `c` is upper diagonal, `r`
    is right hand side and `n` is the size of the system.

    Returns:
    An array of size `n` containing the solution to the
    system of equations.

    """
    res = np.empty(n)
    gam = np.empty(n)

    if b[0] == 0:
        raise RuntimeError("found singular tri-diagonal matrix")

    bet = b[0]
    res[0] = r[0] / bet

    for i in range(1, n):
        gam[i] = c[i - 1] / bet
        bet = b[i] - a[i] * gam[i]

        if bet == 0:
            raise RuntimeError("found singular tri-diagonal matrix")

        res[i] = (r[i] - a[i] * res[i - 1]) / bet

    for i in range(n - 2, -1, -1):
        res[i] = res[i] - gam[i + 1] * res[i + 1]

    return res

import numpy as np
import numba

from .utils import solve_tdma


@numba.njit
def _solve_diffusion_adi_cols(arr_in, arr_out, fact_r, fact_c):
    nr, nc = arr_in.shape

    f = np.zeros(nc)
    diag = np.ones(nc)
    sup = np.zeros_like(f)
    inf = np.zeros_like(f)

    diag[1:-1] = 1 + fact_r * 2
    sup[1:-1] = -fact_r
    inf[1:-1] = -fact_r

    for r in range(1, nr - 1):
        f = (arr_in[r] +
             fact_c * arr_in[r + 1] -
             2 * fact_c * arr_in[r] +
             fact_c * arr_in[r - 1])

        f[0] = arr_in[r, 0]
        f[-1] = arr_in[r, -1]

        arr_out[r] = solve_tdma(inf, diag, sup, f, nc)

    arr_out[0] = arr_in[0]
    arr_out[-1] = arr_in[-1]


def erode_linear_diffusion(erosion, elevation, k_coef,
                           dt, dx, dy, nx, ny):
    """Solve one time step for the linear diffusion equation using
    an Alternate Direction Implicit (ADI) algorithm.

    Using ADI ensures unconditional stability.

    In this first version, the boundary conditions are assumed to be
    fixed elevation on all four boundaries.

    """
    elevation_next = np.empty_like(elevation)

    factx = k_coef * dt * 0.5 / dx**2
    facty = k_coef * dt * 0.5 / dy**2

    _solve_diffusion_adi_cols(elevation,
                              elevation_next,
                              factx, facty)
    _solve_diffusion_adi_cols(elevation_next.transpose().copy(),
                              elevation_next.transpose(),
                              facty, factx)

    erosion[1:-1, 1:-1] = elevation[1:-1, 1:-1] - elevation_next[1:-1, 1:-1]

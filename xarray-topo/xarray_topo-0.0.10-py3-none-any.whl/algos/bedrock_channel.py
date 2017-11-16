import numpy as np
import numba


@numba.njit
def erode_spower(erosion, elevation, stack, receivers, dist2receivers,
                 area, k, m, n, dt, tolerance, nnodes):
    for inode in range(nnodes):
        istack = stack[inode]
        irec = receivers[istack]

        if irec == istack:
            # no erosion at basin outlets
            erosion[istack] = 0.
            continue

        factor = k * dt * area[istack]**m / dist2receivers[istack]**n

        ielevation = elevation[istack]
        irec_elevation = elevation[irec] - erosion[irec]

        # iterate: lower elevation until convergence
        elevation_k = ielevation
        elevation_prev = np.inf

        while abs(elevation_k - elevation_prev) > tolerance:
            slope = elevation_k - irec_elevation
            diff = ((elevation_k - ielevation + factor * (slope)**n) /
                    (1. + factor * n * slope**(n - 1)))
            elevation_k -= diff
            elevation_prev = elevation_k

        erosion[istack] = ielevation - elevation_k

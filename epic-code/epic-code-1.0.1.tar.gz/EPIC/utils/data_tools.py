from __future__ import division 
import numpy as np
from EPIC.utils.math_functions import symmetrize
from EPIC.utils.numbers import dict_sigmaCL

class Lim(object):
    def __init__(self, peaks, count, seps):
        self.xmin = seps[peaks[0]]
        self.xmax = seps[peaks[-1]+1]
        imode = list(count).index(count[peaks[0]:peaks[-1]+1].max())
        self.xmode = (seps[imode] + seps[imode+1]) / 2

class normalLim(object):
    def __init__(self, mu, sigma, level):
        self.mu = mu
        self.sigma = sigma
        self.level = level

def get_min_out(sample, fraction=0.1):
    a = sample.min()
    a -= (sample.max()-a) * fraction
    return a

def get_max_out(sample, fraction=0.1):
    b = sample.max()
    b += (b-sample.min()) * fraction
    return b

def convert_points_errorbars(xmode, xmin, xmax, fmt=None, unit=1):
    x0 = unit * xmode
    if fmt is not None:
        x0 = round(x0, fmt)
    xp = unit * xmax - x0
    xm = x0 - unit * xmin
    return x0, xp, xm

def rounded_asym_errors(xmode, xmin, xmax, fmt=5, unit=1):
    x0, xp, xm = convert_points_errorbars(xmode, xmin, xmax, fmt=fmt,
            unit=unit)
    x0 = x0.__format__(".%if" % fmt)
    xp = xp.__format__(".%if" % fmt)
    xm = xm.__format__(".%if" % fmt)
    return x0, xp, xm

def xmodex1x2CL(LIM, fmt=5, unit=1):
    CL = []
    for cl in LIM:
        if hasattr(cl, 'mu'):
            mu = cl.mu.__format__(".%if" % fmt)
            Lsigma = (cl.sigma * cl.level).__format__(".%if" % fmt)
            CL.append(r'++'.join([mu, Lsigma]))
        else:
            x0 = round(unit * cl.xmode, fmt)
            xp = unit * cl.xmax - x0
            xm = x0 - unit * cl.xmin
            x0, xp, xm = rounded_asym_errors(cl.xmode, cl.xmin, cl.xmax, fmt=fmt,
                    unit=unit)
            if xp == xm:
                CL.append(r'++'.join([x0, xp]))
            else:
                CL.append('%s^{+%s}_{-%s}' % (x0, xp, xm))

    if len(CL) == 1:
        if '++' in CL[0]:
            return CL[0].replace('++', '+')
        else:
            return r'\multicolumn{1}{c}{$' + CL[0] + '$}'
    else:
        CL = [cl.replace('++', r' \pm ') for cl in CL]
        return r'\multicolumn{1}{c}{$' + r' \cup '.join(CL) + '$}'

def get_1D_confidence_regions(count, seps, parfit=None, fmt=5, unit=1, levels=[1, 2], normal=False):
    list_CL = []
    if normal and parfit is not None:
        mu, sig = parfit
    sigmas_up, count = sigmalevels_1D(count, seps, levels=levels)
    for level, sigma_up in zip(levels, sigmas_up):
        if normal:
            LIM = [normalLim(mu, sig, level),]
        else:
            peaks = np.where(count > sigma_up)[0]
            sep_peaks = listsplit(peaks)
            LIM = [Lim(p, count, seps) for p in sep_peaks]
        list_CL.append(xmodex1x2CL(LIM, fmt=fmt, unit=unit))
    return list_CL, sigmas_up


def numpyhist(data, nbins, ws=None, normalize=True):
    H_, b_ = np.histogram(data, weights=ws, bins=nbins, density=normalize)
    w_ = np.diff(b_)
    return H_, b_, w_

def sigmalevels_1D(H, seps, levels=[1, 2]):
    widths = np.diff(seps)
    try:
        assert H.size+1 == seps.size
    except AssertionError:
        H = H[:-1] + np.diff(H)/2
        assert H.size+1 == seps.size
        H /= (H * widths).sum()
    histtype = [('height', float), ('width', float)]
    A = np.array(list(zip(H, widths)), dtype=histtype)
    A = np.sort(A, order='height')
    sorted_H = np.array([a[0] for a in A])
    sorted_w = np.array([a[1] for a in A])
    areas = sorted_H * sorted_w
    limiting = []
    L = np.array([areas[i:].sum() for i in range(A.shape[0])])
    for CL in levels:
        # L is strictly growing, so there will be only one point equal to min(diffL)
        diffL = abs(L - dict_sigmaCL[CL] * areas.sum())
        limiting.append(float(sorted_H[diffL == min(diffL)]))
    return np.array(limiting), H

def sigmalevels_2D(H, xedg, yedg, levels=[1, 2]):
    try:
        assert H.shape[0]+1 == xedg.size
        assert H.shape[1]+1 == yedg.size
    except AssertionError:
        H = H[:,:-1] + np.diff(H, axis=1)/2
        H = H[:-1,:] + np.diff(H, axis=0)/2
        assert H.shape[0]+1 == xedg.size
        assert H.shape[1]+1 == yedg.size
    xwidths = np.array(np.diff(xedg), ndmin=2)
    ywidths = np.array(np.diff(yedg), ndmin=2)
    bases = np.dot(xwidths.transpose(), ywidths)
    arraytype = [('height', float), ('area', float)]
    V = np.array(list(zip(H.transpose().reshape(H.size, 1), bases.reshape(bases.size, 1))), dtype=arraytype)
    V = np.sort(V, order='height')
    sorted_H = np.array([v[0] for v in V])
    sorted_b = np.array([v[1] for v in V])
    volumes = sorted_H * sorted_b
    limiting = []
    L = np.array([volumes[i:].sum() for i in range(V.shape[0])])
    for CL in levels:
        diffL = abs(L - dict_sigmaCL[CL] * volumes.sum())
        limiting.append(float(sorted_H[diffL == min(diffL)]))
    return np.array(limiting), H
    
def listsplit(peaks):
    sep_peaks = []
    aux_peaks = []
    peaks.sort()
    for i, value in enumerate(peaks):
        aux_peaks.append(value)
        try:
            if peaks[i+1]-value>1:
                sep_peaks.append(aux_peaks)
                aux_peaks = []
        except IndexError:
            sep_peaks.append(aux_peaks)
    return sep_peaks

def T_integral_pol(x, a, b, c):
    from scipy.special import erf
    result = np.exp(b**2/4/a - c) * np.sqrt(np.pi) 
    result *= erf((b + 2*a*x)/2/np.sqrt(a))
    result /= 2 * np.sqrt(a)
    return result

def subtract_abc(D1, D2, var1, var2, z):
    a = 1/2 * (1/var1 + 1/var2)
    b = (z-D1.mode)/var1 - D2.mode/var2
    c = 1/2 *((z-D1.mode)**2/var1 + D2.mode**2/var2)
    return a, b, c

def sum_abc(D1, D2, var1, var2, z):
    a = 1/2 * (1/var1 + 1/var2)
    b = - D1.mode/var1 - (z-D2.mode)/var2
    c = 1/2 * (D1.mode**2/var1 + (z-D2.mode)**2/var2)
    return a, b, c

def subtract_point_z(D1, D2, z, x=None):
    # analytical integration of f1(x+z) f2(x) in x from -inf to inf
    abc = subtract_abc(D1, D2, D1.xminus**2, D2.xminus**2, z)
    T1 = T_integral_pol(min(D2.mode, D1.mode-z), *abc) - T_integral_pol(-np.inf, *abc)

    T2 = 0
    T3 = 0
    if D2.mode > D1.mode-z:
        abc = subtract_abc(D1, D2, D1.xplus**2, D2.xminus**2, z)
        T3 += T_integral_pol(D2.mode, *abc) - T_integral_pol(D1.mode-z, *abc)
    elif D2.mode < D1.mode-z:
        abc = subtract_abc(D1, D2, D1.xminus**2, D2.xplus**2, z)
        T2 += T_integral_pol(D1.mode-z, *abc) - T_integral_pol(D2.mode, *abc)

    abc = subtract_abc(D1, D2, D1.xplus**2, D2.xplus**2, z)
    T4 = T_integral_pol(np.inf, *abc) - T_integral_pol(max(D2.mode, D1.mode-z), *abc)

    T_factor = 2 / np.pi / np.prod([D.xminus+D.xplus for D in (D1, D2)])
    return T_factor * (T1 + T2 + T3 + T4)

def sum_point_z(D1, D2, z, x=None):
    # analytical integration of f1(x) f2(z-x) in x from -inf to inf
    T1 = 0
    T4 = 0
    if D1.mode > z - D2.mode:
        abc = sum_abc(D1, D2, D1.xminus**2, D2.xminus**2, z)
        T1 += T_integral_pol(D1.mode, *abc) - T_integral_pol(z - D2.mode, *abc)
    elif D1.mode < z - D2.mode:
        abc = sum_abc(D1, D2, D1.xplus**2, D2.xplus**2, z)
        T4 += T_integral_pol(z - D2.mode, *abc) - T_integral_pol(D1.mode, *abc)

    abc = sum_abc(D1, D2, D1.xminus**2, D2.xplus**2, z)
    T2 = T_integral_pol(min(D1.mode, z-D2.mode), *abc) - T_integral_pol(-np.inf, *abc)

    abc = sum_abc(D1, D2, D1.xplus**2, D2.xminus**2, z)
    T3 = T_integral_pol(np.inf, *abc) - T_integral_pol(max(D1.mode, z-D2.mode), *abc)

    T_factor = 2 / np.pi / np.prod([D.xminus+D.xplus for D in (D1, D2)])
    return T_factor * (T1 + T2 + T3 + T4)

def prod_point_z(D1, D2, z, x):
    import scipy.integrate as integrate
    return integrate.simps(D1.pdf(x) * D2.pdf(z/x) / abs(x), x=x)

def true_divide_point_z(D1, D2, z, x):
    import scipy.integrate as integrate
    return integrate.simps(D1.pdf(x*z) * D2.pdf(x) * abs(x), x=x)

def pdf_convolution(operation, D1, D2, z=None):
    if z is None:
        if operation in ('subtract', 'true_divide'):
            z_sym = np.__getattribute__(operation)(
                    *[symmetrize(D.mode, D.xplus, D.xminus) for D in (D1, D2)])
        else:
            z_sym = np.__getattribute__(operation)(
                    [symmetrize(D.mode, D.xplus, D.xminus) for D in (D1, D2)])
        z = np.linspace(z_sym.nominal_value - 5.5*z_sym.std_dev,
                z_sym.nominal_value + 5.5*z_sym.std_dev,
                1001)

    if operation in ('subtract', 'sum'):
        x = None
    else:
        xa = min([D.mode - 5*D.xminus for D in [D1, D2]])
        xb = max([D.mode + 5*D.xplus for D in [D1, D2]])
        x = np.linspace(xa, xb, 300)

    if isinstance(z, float):
        return z, eval("%s_point_z" % operation)(D1, D2, z, x)
    else:
        return z, np.array([eval("%s_point_z" % operation)(D1, D2, Z, x) for Z in z])


from __future__ import division 
from __future__ import print_function 
import os
import collections
import scipy.stats as st
from scipy.optimize import curve_fit
import numpy as np
import shutil
import uncertainties
import uncertainties.umath as um
import datetime
from scipy.special import erf
import scipy.integrate as integrate
from scipy.interpolate import interp1d
from scipy.optimize import bisect

try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    input = raw_input
except NameError:
    pass

# constants of nature
speedoflight = 299792458. # in m/s
G = 4.3021135e-9 # in units of Mpc Msun**-1 (km/s)**2
mH = 1.67262178e-27 # in units of kg 

# common numbers
log2pi = np.log(2*np.pi)
ln10 = np.log(10)

# units conversion
keV = 1.602176565e-22 # in units of kg (km/s)**2
kg = 1/keV # in units of keV (km/s)**-2
mumH = mH * kg * 0.63
GmumH = G * mumH

# statistics
scipy_stats_standard_normal = st.distributions.norm(0, 1)
CL68 = 0.682689492137086
CL95 = 0.954499736103642
CL997 = 0.997300203936740
CL999 = 0.999936657516334

#dict_sigmaCL = lambda n: 1 - 2 * scipy_stats_standard_normal.cdf(-n)
dict_sigmaCL = dict(zip(range(1, 5), [CL68, CL95, CL997, CL999]))

# some definitions for plots
alphas = [0.70, 0.35, 0.15]
#alpha1s = 0.70 #.40
#alpha2s = 0.35 #.25
superposalpha = min(alphas[0] + alphas[1], 1)
kde_numpoints = 500
kde2d_numpoints = 150

class Prior(object):
    def __init__(self, vmin, vmax, vdefault):
        self.vmin = vmin
        self.vmax = vmax
        self.ref = vdefault
        self.interval_size = vmax - vmin

    def __repr__(self):
        return ',\t'.join(("%.3e" % self.vmin, "%.3e" % self.vmax, "%.3e" % self.ref))

class GaussianPrior(object):
    def __init__(self, mu, sigma):
        self.mu = float(mu)
        self.sigma = float(sigma)
        self.vmin = self.mu - 6 * self.sigma
        self.vmax = self.mu + 6 * self.sigma
        self.ref = self.mu
        self.interval_size = self.vmax - self.vmin

    def __repr__(self):
        return 'N(%.3e, %.3e)' % (self.mu, self.sigma)

class Fixed(object):
    def __init__(self, value):
        self.vmin = value
        self.vmax = value
        self.ref = value

    def __repr__(self):
        return ',\t'.join(("%.3f" % self.vmin, "%.3f" % self.vmax, "%.3f" % self.ref))

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

def rho_critical(Hz):
    return 3*Hz**2/(8*np.pi*G)    # h^2 Msun Mpc^-3

def T_integral_pol(x, a, b, c):
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
    return integrate.simps(D1.pdf(x) * D2.pdf(z/x) / abs(x), x=x)

def true_divide_point_z(D1, D2, z, x):
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

class MixedDist(object):
    def __init__(self, xmode, xmin, xmax, NUM=None):
        self.lower_lim = xmin
        self.upper_lim = xmax
        self.mode, self.xplus, self.xminus = convert_points_errorbars(xmode, xmin,
                xmax, fmt=None, unit=1)
        self.ampl_m = 2 * self.xminus / (self.xminus + self.xplus)
        self.ampl_p = 2 * self.xplus  / (self.xminus + self.xplus)

    def pdf(self, x):
        x = np.array(x)
        return np.where(
                x < self.mode,
                self.ampl_m * scipy_stats_standard_normal.pdf((x-self.mode)\
                        /self.xminus)/self.xminus, 
                self.ampl_p * scipy_stats_standard_normal.pdf((x-self.mode)\
                        /self.xplus)/self.xplus
                )

    def cdf(self, x):
        x = np.array(x)
        return np.where(
                x < self.mode,
                self.ampl_m * scipy_stats_standard_normal.cdf((x-self.mode)\
                        /self.xminus),
                self.ampl_p * scipy_stats_standard_normal.cdf((x-self.mode)\
                        /self.xplus)
                )

    def rvs(self, num=200000):
        np.random.seed()
        num_m = int(2*num * self.ampl_m)
        Zm = np.random.normal(size=num_m)
        Zm = Zm[Zm < 0]
        num_p = int(2*num * self.ampl_p)
        Zp = np.random.normal(size=num_p)
        Zp = Zp[Zp > 0]
        Z = np.concatenate([Zm, Zp])
        Z = Z[Z < 4] 
        Z = Z[Z > -4]
        np.random.shuffle(Z)
        Z = Z[:num]
        R = self.mode + Z * np.where(Z <= 0, self.xminus, self.xplus)
        return R

    def use_sample(self, a=None, b=None, num=10000):
        if hasattr(self, '_sample'):
            self_sample = self._sample
        else:
            self._sample = self.rvs(num=num)
            if a is not None:
                while self._sample[self._sample < a].size > 0:
                    new_samples = self.rvs(num=self._sample[self._sample < a].size)
                    self._sample = np.concatenate(
                            [self._sample[self._sample >= a], new_samples])
            if b is not None:
                while self._sample[self._sample > b].size > 0:
                    new_samples = self.rvs(num=self._sample[self._sample > b].size)
                    self._sample = np.concatenate(
                            [self._sample[self._sample <= b], new_samples])
            self_sample = self._sample
        return self_sample

    def __add__(self, other):
        if isinstance(other, MixedDist):
            z, function_sum = pdf_convolution('sum', self, other)
            fit = fit_asymmetrical(None, kdefit_asym=(z, function_sum))
            return MixedDist(*fit)
        else:
            return MixedDist(
                    self.mode + other,
                    self.lower_lim + other,
                    self.upper_lim + other,
                    )

    def __radd__(self, other):
        return self.__add__(other)

    def __mul__(self, other):
        if isinstance(other, MixedDist):
            z, function_prod = pdf_convolution('prod', self, other)
            fit = fit_asymmetrical(None, kdefit_asym=(z, function_prod))
            return MixedDist(*fit)
        else:
            if other == 0:
                return 0
            elif other > 0:
                return MixedDist(
                        other * self.mode,
                        other * self.lower_lim,
                        other * self.upper_lim
                        )
            else:
                return MixedDist(
                        other * self.mode,
                        other * self.upper_lim,
                        other * self.lower_lim,
                        )

    def __rmul__(self, other):
        return self.__mul__(other)

    def __sub__(self, other):
        if isinstance(other, MixedDist):
            z, function_subtract = pdf_convolution('subtract', self, other)
            fit = fit_asymmetrical(None, kdefit_asym=(z, function_subtract))
            return MixedDist(*fit)
        else:
            return MixedDist(
                    self.mode - other,
                    self.lower_lim - other,
                    self.upper_lim - other
                    )

    def __rsub__(self, other):
        if isinstance(other, MixedDist):
            return other.__sub__(self)
        else:
            return MixedDist(
                    other - self.mode,
                    other - self.upper_lim,
                    other - self.lower_lim,
                    )

    def __truediv__(self, other):
        if isinstance(other, MixedDist):
            z, function_true_divide = pdf_convolution('true_divide', self, other)
            fit = fit_asymmetrical(None, kdefit_asym=(z, function_true_divide))
            return MixedDist(*fit)
        else:
            return self.__mul__(1./other)

    def __rtruediv__(self, other):
        if isinstance(other, MixedDist):
            return other.__truediv__(self)
        else:
            array = other/self.use_sample()
            array = array[~np.isnan(array)]
            return MixedDist(*fit_asymmetrical(array))

    def __pow__(self, other):
        if isinstance(other, MixedDist):
            array = self.use_sample() ** other.use_sample()
            array = array[~np.isnan(array)]
            return MixedDist(*fit_asymmetrical(array))
        else:
            if other == 0:
                return 1
            elif isinstance(other, int):
                power = np.prod([self for _ in range(abs(other))])
                if other > 0:
                    return power
                else:
                    return 1/power
            else:
                array = self.use_sample() ** other
                array = array[~np.isnan(array)]
                return MixedDist(*fit_asymmetrical(array))

    def __rpow__(self, other):
        array = other ** self.use_sample()
        array = array[~np.isnan(array)]
        return MixedDist(*fit_asymmetrical(array))

    def __str__(self):
        return ": %.3e, %.3e, %.3e" % (
                self.mode, 
                self.xplus, 
                self.xminus,
                )

class Bivariate_Normal(object):
    def __init__(self, Mu, Cov, factor=None):
        [a, b], [c, d] = np.array(Cov)
        self.Mu = np.array(Mu)
        self.detCov = a*d - b*c
        self.ICov = 1/self.detCov * np.array([[d, -b], [-c, a]])
        if factor is not None:
            self.detCov *= factor*factor
            self.ICov /= factor
        self.mvn_factor = 1/(2*np.pi)/np.sqrt(self.detCov)

    def pdf(self, support):
        support = np.array(support)#, ndmin=2)
        results = [ - 1/2 * np.dot( np.dot(sup-self.Mu, self.ICov), (sup-self.Mu).transpose()) for sup in support]
        if len(results) == 1:
            return self.mvn_factor * np.exp(results)[0]
        else:
            return self.mvn_factor * np.exp(results)

def fc_gc_dFdc_from_c(c):
    one_plus_c = 1+c
    two_plus_c = 2+c
    c_squared = c*c
    try:
        log_one_plus_c = um.log(one_plus_c)
    except TypeError:
        log_one_plus_c = np.log(one_plus_c)
    one_plus_c__times__log_opc = one_plus_c * log_one_plus_c
    one_plus_c__times__logsquare = one_plus_c__times__log_opc * log_one_plus_c
    fc = one_plus_c__times__logsquare - 2 * c * log_one_plus_c
    fc = fc + one_plus_c * c_squared / one_plus_c**2
    fc = fc / c / (0.5*(one_plus_c- 1/one_plus_c) - log_one_plus_c)

    dFdc = 2 * (one_plus_c__times__log_opc - c) 
    dFdc = dFdc * (c*(4+5*c+c_squared) * log_one_plus_c -c_squared *(2+3*c) - 2 * one_plus_c__times__logsquare)
    dFdc = -1 * dFdc /(c_squared * (c *two_plus_c-2*one_plus_c__times__log_opc)**2)
    return fc, dFdc

def general_average_std(values, weights=None):
    ave = np.average(values, weights=weights)
    var = np.average((values-ave)**2, weights=weights)
    return ave, np.sqrt(var)

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

def fit_asymmetrical(sample, nbins=140, kdefit_asym=False, THIN=None):
    if kdefit_asym is False:
        count, seps, widths = numpyhist(sample, nbins)
        sample_totallength = len(sample)
        normalization = sample_totallength * (seps[-1]-seps[0])/len(count)
        count = np.array(count) * normalization
        onesigma, count = sigmalevels_1D(count, seps, levels=[1,])
        peaks1s = np.where(count > onesigma)[0]
        sep_peaks_1s = listsplit(peaks1s)
        #print(len(sep_peaks_1s))
        #print(sep_peaks_1s, onesigma, peaks1s)
        #print(onesigma, count)
        cl = Lim(sep_peaks_1s[0], count, seps)
        #plt.fill_between(x, 0, mix_dist.pdf(x), where=np.where(mix_dist.pdf(x) > onesigma/normalization, True, False), alpha=0.4)
        return cl.xmode, cl.xmin, cl.xmax
    elif kdefit_asym == 'lognormal':
        logsample = np.log(sample)
        LN = st.distributions.lognorm(logsample.std(), scale=np.exp(logsample.mean()))
        xa, xb = sample.min(), sample.max()
        amp = xb - xa
        x = np.linspace(sample.min() - amp/10, sample.max() + amp/10, 1001)
        return fit_asymmetrical(None, kdefit_asym=(x, LN.pdf(x)))
    else:
        support, kde_orig = make_kde([sample,], thin=THIN) if kdefit_asym is True else kdefit_asym
        try:
            onesigma, kde = sigmalevels_1D(kde_orig, support, levels=[1,])
            peaks1s = np.where(kde > onesigma)[0]
            sep_peaks_1s = listsplit(peaks1s)[0]
            clmin = support[sep_peaks_1s[0]]
            clmax = support[sep_peaks_1s[-1]]
            interval = kde[sep_peaks_1s[0]:sep_peaks_1s[-1]]
            interval = sorted(interval)[::-1]
            imode = [list(kde).index(value) for value in interval[:5]]
            clmode = np.mean([support[i] for i in imode])
            #imode = list(kde).index(kde[sep_peaks_1s[0]:sep_peaks_1s[-1]].max())
            #clmode = support[imode]
        except ValueError:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots()
            ax.plot(support, kde_orig, lw=0.5, color='r')
            fig.savefig('debug_fitasym.pdf')
            raise ValueError
        return clmode, clmin, clmax

def fixed_length(label, windowsize=False, fill_char=' ', barwidth=10, barlength=20):
    if not windowsize:
        try:
            import curses
            curses.setupterm()
            windowsize = curses.tigetnum("cols")
        except:
            windowsize=80
    windowsize = min(windowsize, 80)
    freespace = -1
    origlabel = label
    i = len(label)
    while freespace < 0:
        label = label[:i]
        if i < len(origlabel):
            label = label[:-3] + '...'
        freespace = windowsize - len(label) - barwidth - 2 - 2 - 2
        show_pos  = 1 + 2*len(str(barlength))
        show_percent = 4
        freespace -= max(show_pos, show_percent)
        i -= 1
    return label + freespace//len(fill_char) * fill_char

def get_inifile_name(wdir):
    inifile = os.listdir(wdir)
    inifile = [df for df in inifile if not '.swp' in df]
    inifile = [df for df in inifile if not '.un~' in df]
    return lookargext('.ini', inifile)

def read_model_name(wdir, label='NAME'):
    inifile = get_inifile_name(wdir)
    return read1linestring(readfile(os.path.join(wdir, inifile)), label)

def saveint(filename, value):
    with open(filename, 'w') as wf:
        wf.write("%i\n" % value)

def readint(filename):
    with open(filename, 'r') as wf:
        integer = wf.readline().strip()
    return int(integer)

def find_timestring_convert_to_seconds(arg):
    value = re_lookarg('\d+h', arg)  # time in hours preferable over min
    if value:
        value = int(value[:-1])
        return value * 60 * 60 # time from hours to seconds
    else:
        value = re_lookarg('\d+min', arg)
        if value:
            value = int(value[:-3])
            return value * 60 # time from minutes to seconds
        else:
            value = re_lookarg('\d+sec', arg)
            if value:
                return int(value[:-3])
            else:
                return False

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

def CL_excluding_value_kde(support, kde1, exclude=0.0):
    ikde = interp1d(support, kde1)
    try:
        k_exclude = ikde(exclude)
        if exclude not in support:
            newsupport = np.concatenate([support[support < exclude], [exclude,],
                support[support > exclude]])
            kde1 = np.concatenate([kde1[support < exclude], [k_exclude,],
                kde1[support > exclude]])
        percent = integrate.trapz(
                kde1[kde1 >= k_exclude], 
                x=newsupport[kde1 >= k_exclude]
                )/ integrate.trapz(kde1, x=newsupport)
    except ValueError:
        percent = integrate.trapz(kde1, x=support)
    return scipy_stats_standard_normal.ppf(percent/2+0.5)

def CL_excluding_value_data(sample, exclude=0.0):
    return CL_excluding_value_kde(*make_kde([sample,], thin=1), exclude=exclude)

def exponential_corr(x, tau):
    return np.exp(-x/tau)

def double_Gaussian(x, mu1, sig1, mu2, sig2, A):
    pdf = A/sig1 * np.exp(-1/2 * ((x-mu1)/sig1)**2) +\
            (1-A)/sig2 * np.exp(-1/2 * ((x-mu2)/sig2)**2)
    return pdf/np.sqrt(2*np.pi)

def sample_variance(x):
    return sample_covariance(x, x)

def sample_covariance(x, y):
    assert x.size == y.size
    X = x - x.mean()
    Y = y - y.mean()
    cov = (np.sum(X*Y) - X.sum() * Y.sum() / X.size) / X.size
    return cov

def correlation(X, Y, j):
    Xbar, Ybar = X.mean(), Y.mean()
    SX, SY = X.size, Y.size
    assert SX == SY
    rho = np.sum( (X[:SX-j]-Xbar) * (Y[j:]-Ybar) )
    rho /= np.sqrt( np.sum( (X[:SX-j]-Xbar)**2 ) )
    rho /= np.sqrt( np.sum( (Y[j:]-Ybar)**2 ) )
    return rho

def auto_correlation(X, j):
    return correlation(X, X, j)

#def auto_correlation(X, j):
#    Xbar = X.mean()
#    S = X.size
#    rho = np.sum( (X[:S-j]-Xbar) * (X[j:]-Xbar) )
#    rho /= np.sqrt( np.sum( (X[:S-j]-Xbar)**2 ) )
#    rho /= np.sqrt( np.sum( (X[j:]-Xbar)**2 ) )
#    return rho

def fit_tau(time, listcorr, P):
    popt, _ = curve_fit(exponential_corr, xdata=time, ydata=listcorr, p0=P)
    return popt[0]

#def two_peak_gaussian(x, mu1, sigma1, w1, mu2, sigma2, w2):
#    return w1 * st.distributions.norm(mu1, sigma1).pdf(x) + \
#            w2 * st.distributions.norm(mu2, sigma2).pdf(x)

#def fit_multipeak_gaussians(X, H):
#    popt, _ = curve_fit(two_peak_gaussian, xdata=X, ydata=H)
#    return popt

def z_of_a(A):
    return 1/A - 1

def draw_ellipse(InvFisher, means, CLsigma=1, precision=200):
    assert np.shape(InvFisher) == (2, 2)
    sigx2 = InvFisher[0, 0]
    sigy2 = InvFisher[1, 1]
    sigxy2 = InvFisher[0, 1]

    a = np.sqrt( 0.5 * (sigx2 + sigy2) + np.sqrt( 0.25 * (sigx2 - sigy2)**2 + sigxy2**2))
    b = np.sqrt( 0.5 * (sigx2 + sigy2) - np.sqrt( 0.25 * (sigx2 - sigy2)**2 + sigxy2**2))
    phi0 = 0.5 * np.arctan2( 2*sigxy2 , (sigx2 - sigy2) )

    x0, y0 = means

    if isinstance(CLsigma, int):
        alphaCL = CLsigma/2
    else:
        alphaCL = st.distributions.chi2(2).ppf(CLsigma)/2

    phi = np.linspace(0, np.pi*2, precision)
    thetax = alphaCL * (a * np.cos(phi) * np.cos(phi0) - b * np.sin(phi) * np.sin(phi0)) + x0
    thetay = alphaCL * (a * np.cos(phi) * np.sin(phi0) + b * np.sin(phi) * np.cos(phi0)) + y0
        
    return thetax, thetay    

def create_listbinsdict(wdir, combobins, binsfile, clear=False):
    listbins = []
    for cb in combobins:
        binsdict = {'default':  cb}
        if binsfile:
            binsdict = load_bins(binsfile, binsdict, cb)
        listbins.append(binsdict)
        pasta(wdir, "results%i" % cb, clear=clear)
    return listbins

def load_bins(binsfile, binsdict, cbins):
    lines = readfile(binsfile)

    l = iter(lines)
    a = next(l)
    while l and (not 'BINS' in a):
        a = next(l)
    while l and (not 'end' in a):
        if (not a[0] == '#') and len(a.split()) == 2:
            key, wbins = a.split()
            binsdict[key] = int(round(float(wbins)*cbins))
        a = next(l)
    return binsdict

def load_chains_and_model_details(wdir):
    priors = pickle.load(open(os.path.join(wdir, 'priors.p'), 'rb'))
    nuisance = pickle.load(open(os.path.join(wdir, 'nuisance.p'), 'rb'))
    mq = pickle.load(open(os.path.join(wdir, 'mq.p'), 'rb'))
    tex = pickle.load(open(os.path.join(wdir, 'tex.p'), 'rb'))
    for par in tex.keys():
        tex[par] = tex[par].replace('text', 'mathrm')
    parnames = pickle.load(open(os.path.join(wdir, 'parnames.p'), 'rb'))
    nparams = readint(os.path.join(wdir, 'nparams.txt'))
    nchains = readint(os.path.join(wdir, 'nchains.txt'))
    return priors, nuisance, mq, tex, parnames, nparams, nchains

def format_with_uncertainties(list_pars, wdirn, ffile, fmt='.5e'):
    with open(os.path.join(wdirn, ffile), 'w') as fitfile:
        for fit in list_pars:
            nom, dev = fit
            fitfile.write(uncertainties.ufloat(nom, dev).format('.5e').replace('/-','') + '\n')

def Information_Criteria(n, parnames, bestfit, priors, nparams, nnuis, maxlogposterior, workingdir, b=None):
    if b is None:
        suffix = "n%i" % n
    else:
        suffix = "n%ib%i" % (n, b)
    params = dict(zip(parnames, bestfit))
    maxloglikelihood = maxlogposterior - logpriordist(params, priors)
    #if __name__ == '__main__':
    #    print('maxlogposterior', maxlogposterior)
    #    print('log prior BF', logpriordist(params, priors))
    AIC = -2 * maxloglikelihood + 2 * (nparams-nnuis)
    np.savetxt(os.path.join(workingdir, suffix, 'AIC.txt'), (AIC,))
    nBIC = readint(os.path.join(workingdir, 'nBIC.txt'))
    BIC = -2 * maxloglikelihood + np.log(nBIC) * (nparams-nnuis)
    np.savetxt(os.path.join(workingdir, suffix, 'BIC.txt'), (BIC,))
    return AIC, BIC

def corr_to_cov(sigmas, corr):
    S = np.array([sigmas for _ in sigmas])
    covs = S.transpose() * S
    return covs * corr

def cov_to_corr(M):
    dM = np.diag(M)
    C = np.array([dM for _ in dM])
    pC = C.transpose() * C
    return M/np.sqrt(pC)

def det(A):
    sign, logdet = np.linalg.slogdet(A)
    return sign * np.exp(logdet)

def symmetrize(x, x1, x2=None):
    if x2:
        return uncertainties.ufloat(x+0.8*(x1-x2), (x1+x2)/2) 
    else:
        # can't just return the same as above because would give x1/2
        return uncertainties.ufloat(x, x1)

def if_not_given(dictio, dictio2, name, value=None):
    try:
        return dictio[name]
    except KeyError:
        try:
            return dictio2[name]
        except KeyError:
            return value 

def assert_extension(name, ext):
    ext = '.' + ext
    if name.endswith(ext):
        return name
    else:
        return name + ext

def re_lookarg(pattern, list_argv):
    import re
    p = re.compile(pattern)
    for arg in list_argv:
        if p.match(arg):
            return arg
    else:
        return False

def lookarg(string, list_argv):
    for arg in list_argv:
        if string in arg:
            returnFound = arg
            break
    else:
        returnFound = False
    return returnFound

def lookarg1(string, list_argv, instance=None, optask=None):
    findres = lookarg(string, list_argv)
    if findres:
        if instance:
            return instance(findres.split('=')[1])
        else:
            return findres.split('=')[1]
    else:
        if optask:
            return instance(input(optask))
        else:
            return findres

def lookargext(string, list_argv):
    findres = lookarg(string, list_argv)
    return assert_extension(findres, string[-3:])

def lookarg1list(string, list_argv, instance=None, optask=None):
    findres = lookarg1(string, list_argv, optask=optask)
    if findres:
        if instance:
            return [instance(fr) for fr in findres.split(',')]
        else:
            return [fr for fr in findres.split(',')]
    else:
        return findres

def lookprior(inifile_lines, needs_mq=True):
    l = iter(inifile_lines)
    a = next(l)
    params = collections.OrderedDict()
    mq = collections.OrderedDict()
    nuisance = []
    while l and (not 'end' in a):
        slices = a.split()
        if len(slices) > 0 and not a[0] == '#':
            key = slices.pop(0)
            Nlist = [s for s in slices if 'N=' in s]
            # this is for retrocompatibility with old files which had a N=1000 column (grid)
            if len(Nlist) > 0:
                for element in Nlist:
                    slices.remove(element) # just ignore the Nphasespace number for the MCMC
            if 'nuisance' in slices:
                nuisance.append(key)
                slices.remove('nuisance')
            #if len(slices) == 3: # asymmetrical error
            #    pvalue, dx1, dx2 = slices
            #    params[key] = Prior(float(pvalue)-float(dx2), float(pvalue)+float(dx1), float(pvalue))

            if 'gaussian' in slices:
                nonflat = True
                slices.remove('gaussian')
            else:
                nonflat = False

            if len(slices) == 1: # fixed parameter
                pvalue = slices
                params[key] = Fixed(float(pvalue[0]))
            elif len(slices) == 3: # mq value
                mq[key] = float(slices.pop(-1))

            if len(slices) == 2: # plus/minus delta
                pmin, pmax = slices
                if nonflat:
                    params[key] = GaussianPrior(pmin, pmax)
                    if not key in mq:
                        mq[key] = float(pmax)
                else:
                    pdefault = (float(pmin) + float(pmax))/2
                    params[key] = Prior(float(pmin), float(pmax), pdefault) 
                if not key in mq and needs_mq:
                    mq[key] = float(input('Enter mq value for parameter %s: ' % key))

            if len(slices) > 3:
                raise

        a = next(l)
    return params, nuisance, mq

def printtime(time):
    if time < 60:
        return '%.1f seconds' % time
    else:
        if time < 60*60:
            return '%im%is' % divmod(time,60)
        else:
            if time < 60*60*24:
                return '%ih%im' % divmod(time/60,60)
            else:
                return '%id%.1fh' % divmod((time/60)/60, 24)

# file reading

def loadtxt(filename, wdir, I):
    #import numpy as np
    p = open(os.path.join(wdir, 'previous%i.txt' % (I+1)), 'r')
    previous = p.readline()
    previous = int(previous.strip('\n'))
    p.close()

    f = open(filename, 'r')
    lines = f.readlines()
    R = previous+1 - int(lines[-1].strip('\n').split(',')[-1])
    f.close()

    shutil.copy2(filename, os.path.join(wdir, 'taux%i.txt' % (I+1)))
    g = open(os.path.join(wdir, 'taux%i.txt' % (I+1)), 'a')
    g.write(', %i' % R)
    g.close()

    numpytxt = np.loadtxt(os.path.join(wdir, 'taux%i.txt' % (I+1)), delimiter=',')
    os.remove(os.path.join(wdir, 'taux%i.txt' % (I+1)))
    return numpytxt

def readfile(filename):
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read1linestring(datalines, label):
    l = iter(datalines)
    a = next(l)
    while l and (not label in a):
        a = next(l)
    a = next(l)
    return a.strip()

def readlegend(iterable, nparams, I):
    text = r'' + next(iterable).split('\t')[1].strip('\n')
    for j in range(nparams-I-1): # I the number of integrated (marginalized) paramenters, the other in the line above
        text = text + '\n' + next(iterable).strip('\n')
    return text

def looktagstrings(inifile_lines, tag):
    l = iter(inifile_lines)
    a = next(l)
    while l and (not tag in a):
        a = next(l)
    dicttag = collections.OrderedDict()
    while l and (not 'end' in a):
        if not a[0] == '#' and len(a.split()) == 2:
            key, string = a.split()
            dicttag[key] = string
        a = next(l)
    return dicttag

# folder manipulation

def deletefiles(folder):
    dirPath = os.path.join( os.path.abspath(os.path.curdir), folder )
    fileList = os.listdir( dirPath )
    for fName in fileList:
        os.remove( os.path.join( dirPath, fName ) )

def getfilelist(folder, ext):
    fl = os.listdir(folder)
    dext = '.' + ext
    fl = [FL for FL in fl if FL.endswith(dext)]
    return fl

def pasta(local, horario, clear=False):
    criar = os.path.join(local, horario)
    if not os.path.isdir( criar ):
        os.mkdir( criar )
    if clear:
        deletefiles( criar )
    return criar

def define_time():
    return datetime.datetime.utcnow().strftime("%y%m%d-%H%M%S")

# statistics

def normalize(h, origlims, newlims=(0, 1)):
    P1, P2 = newlims
    H1, H2 = origlims
    return (h - H1)/(H2 - H1) * (P2 - P1) + P1

class ListDistributions(object):
    def __init__(self, listD):
        self.listD = listD

    def rvs(self):
        return np.array([l.rvs() for l in self.listD])   

    def pdf(self, X):
        return np.array([l.pdf(X) for l in self.listD])

def uniform(u, v):
    return 1/(v-u)

def logpriordist(params, priors):
    logpriorpdf = {}
    for par in params:
        #x = params[par]
        #mu = priors[par].ref
        #sigma = (priors[par].vmax - priors[par].vmin) / 2.
        #logpriorpdf[par] = np.log(1./sigma/np.sqrt(2*np.pi)) - (x-mu)**2/2./sigma**2 # gaussian priors
        if hasattr(priors[par], 'mu'):
            logpriorpdf[par] = np.log(1/priors[par].sigma \
                    * scipy_stats_standard_normal.pdf(
                        (params[par] - priors[par].mu)/priors[par].sigma
                        ))
        else:
            if priors[par].vmin <= params[par] <= priors[par].vmax:
                logpriorpdf[par] = np.log(uniform(priors[par].vmin, priors[par].vmax)) # flat priors
            else:
                logpriorpdf[par] = -np.inf
    return sum([logpriorpdf[par] for par in params])

def MVUdistribution(X, S):
    Y = [st.uniform(x-s, 2*s) for (x, s) in zip(X, S)]
    return ListDistributions(Y)

def MVNdistribution(X, S):
    '''
    Multivariate Normal Distribution
    S is the covariance matrix
    '''
    Y =  st.multivariate_normal(X, S)
    return Y

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

#posterior
def test_p(X):
    s8dist = st.distributions.norm(0.8, 0.05)
    w0dist = st.distributions.norm(-1, 0.2)
    Omdist = st.distributions.norm(0.27, 0.03)
    # X is an 1-D array
    P = s8dist.pdf(X[0]) * w0dist.pdf(X[1]) * Omdist.pdf(X[2])
    return P

# plot

def get_min_out(sample, fraction=0.1):
    a = sample.min()
    a -= (sample.max()-a) * fraction
    return a

def get_max_out(sample, fraction=0.1):
    b = sample.max()
    b += (b-sample.min()) * fraction
    return b

def thin_factor(sample_size, desired_order=4):
    thin = max(0, int(round(np.log10(sample_size) - desired_order)))
    thin = max(1, 10**thin//2)
    return thin, sample_size//thin

def make_kde(samples, x=None, a_support=None, b_support=None, a_edg=None,
        b_edg=None, bandwidth=None, support_file=None, density_file=None,
        thin=None, correct_boundaries=False, normalization=None,
        kde_shuffle=False, bar=None):

    if x is None:
        supports = []
    densities = []
    thin_samples = []
    samples_norm = []
    samples_std = []

    for sample in samples:
        this_sample_thin = thin or thin_factor(sample.size)[0]
        if kde_shuffle:
            np.random.shuffle(sample)
        sample = sample[::this_sample_thin]
        thin_samples.append(sample)
        this_sample_normalization = np.ones_like(sample) if normalization is None else normalization
        samples_norm.append(this_sample_normalization)
        std = general_average_std(sample, weights=this_sample_normalization)[1]
        samples_std.append(std)
        if x is None:
            this_sample_a_support = get_min_out(sample) if a_support is None else a_support
            this_sample_b_support = get_max_out(sample) if b_support is None else b_support
            numpoints_factor = max(1, (this_sample_b_support-this_sample_a_support)/std) 
            support = np.linspace(this_sample_a_support, this_sample_b_support, int(round(numpoints_factor * kde_numpoints)))
            supports.append(support)

    if x is None:
        support = np.concatenate(supports)
        support.sort()
        x_or_support = support
    else:
        x_or_support = np.array(x, ndmin=1)

    for sample, norm, std in zip(thin_samples, samples_norm, samples_std):
        this_sample_bandwidth = bandwidth or std
        this_sample_bandwidth *= (4/3/sample.size)**(1/5)
        normX = st.distributions.norm(0, this_sample_bandwidth)
        density = np.zeros_like(x_or_support)
        if correct_boundaries:
            for X, n in zip(sample, norm):
                density += n/3 * (
                        normX.pdf(x_or_support-X) +\
                                normX.pdf(2*a_edg-x_or_support-X) +\
                                normX.pdf(2*b_edg-x_or_support-X)
                                )
        else:
            for X, n in zip(sample, norm):
                density += n * normX.pdf(x_or_support-X)
        # this offers a quicker but not optimal boundary correction when parameter
        # is weakly constrained (flat distribution):
        ##kernels = [kern/ integrate.simps(kern, x=support) for kern in kernels]

        densities.append(density)

    density = np.sum(densities, axis=0)
    if x is None:
        density /= integrate.simps(density, x=x_or_support) # or trapz
    else:
        density /= np.sum([sample.size for sample in thin_samples])

    if support_file:
        np.savetxt(support_file, x_or_support)
    if density_file:
        np.savetxt(density_file, density)
    if bar:
        bar.update(1)
    return x_or_support, density

def reshape_3d_2d(support):
    shapex, shapey, shapez = support.shape
    assert shapez == 2
    return shapex, shapey, support.reshape(shapex*shapey, shapez)

def make_kde2d(xsamples, ysamples, xa_support=None, xb_support=None,
        ya_support=None, yb_support=None, xa_edg=None, xb_edg=None,
        ya_edg=None, yb_edg=None, bandwidth=None, xsupport_file=None,
        ysupport_file=None, density_file=None, thin=None,
        correct_boundaries=False, normalization=None, numpoints=None,
        bar=None):
    from scipy import integrate

    densities = []
    array_supports = {'x': [], 'y': []}
    thin_samples = {'x': [], 'y': []}
    Asupport = {}

    for xysample in zip(xsamples, ysamples):
        for xy, sample, a_support, b_support in zip(
                ('x', 'y'),
                xysample, 
                (xa_support, ya_support), 
                (xb_support, yb_support)
                ):
            this_sample_a_support = get_min_out(sample) if a_support is None else a_support
            this_sample_b_support = get_max_out(sample) if b_support is None else b_support
            this_sample_thin = thin or thin_factor(sample.size)[0]
            sample = sample[::this_sample_thin]
            thin_samples[xy].append(sample)
            u = np.linspace(this_sample_a_support, this_sample_b_support, kde2d_numpoints)
            array_supports[xy].append(u)

    for xy in ('x', 'y'):
        # must be uniformly spaced
        Asupport[xy] = np.linspace(np.min(array_supports[xy]), np.max(array_supports[xy]), num=np.size(array_supports[xy]))
        #Asupport[xy] = np.concatenate(array_supports[xy])
        #Asupport[xy].sort()

    support = np.array([[(X, Y) for Y in Asupport['y']] for X in Asupport['x']])
    shapex, shapey, support_reshaped = reshape_3d_2d(support)

    for xysample in zip(thin_samples['x'], thin_samples['y']):
        this_sample_normalization = np.ones_like(xysample[0]) \
                if normalization is None else normalization
        assert xysample[0].size == xysample[1].size
        bw_factor = (1/xysample[0].size)**(1/3)
        these_samples_bandwidth = np.cov(*xysample) if bandwidth is None else bandwidth
        these_samples_bandwidth *= bw_factor

        try:
            mvn = st.multivariate_normal([0, 0], these_samples_bandwidth)
        except (np.linalg.LinAlgError, ValueError):
            mvn = Bivariate_Normal([0, 0], these_samples_bandwidth)

        if correct_boundaries:
            density = reflected_bivariate_normal(support_reshaped, xa_edg,
                    xb_edg, ya_edg, yb_edg, mvn, xysample[0], xysample[1],
                    shapex, shapey, this_sample_normalization)
        else:
            density = np.zeros((shapex, shapey))
            for s in zip(xysample[0], xysample[1], this_sample_normalization):
                density += np.reshape(
                        s[2] * mvn.pdf(support_reshaped - s[:2]),
                        (shapex, shapey)
                        )

        densities.append(density)

    density = np.sum(densities, axis=0)
    density /= integrate.simps(integrate.simps(density, x=Asupport['y']), x=Asupport['x'])
    if xsupport_file:
        np.savetxt(xsupport_file, Asupport['x'])
    if ysupport_file:
        np.savetxt(ysupport_file, Asupport['y'])
    if density_file:
        np.savetxt(density_file, density)
    if bar:
        bar.update(1)
    return Asupport['x'], Asupport['y'], density

def reflected_bivariate_normal(support, xa, xb, ya, yb, mvn, xsample, ysample,
        shapex, shapey, normalization):
    xa_reflection = np.array([[2*xa - sup[0], sup[1]] for sup in support])
    xb_reflection = np.array([[2*xb - sup[0], sup[1]] for sup in support])
    ya_reflection = np.array([[sup[0], 2*ya - sup[1]] for sup in support])
    yb_reflection = np.array([[sup[0], 2*yb - sup[1]] for sup in support])
    density = np.zeros((shapex, shapey))
    for s in zip(xsample, ysample, normalization):
        density += np.reshape(s[2]/5 * (
            mvn.pdf(support-s[:2]) + mvn.pdf(xa_reflection-s[:2]) +\
                    mvn.pdf(xb_reflection-s[:2]) + mvn.pdf(ya_reflection-s[:2]) +\
                    mvn.pdf(yb_reflection-s[:2])
                    ), (shapex, shapey)
                    )
    return density

def make_kde_star(args):
    return make_kde(*args)

def make_kde2d_star(args):
    return make_kde2d(*args)

def create_tex_table(file_path, cfont=None):
    texfile = open(file_path, 'w')
    latex_lines = [
            r'\documentclass[landscape]{revtex4-1}',
            r'\usepackage{mathtools}',
            r'\usepackage{dcolumn}',
            r'\usepackage{siunitx}',
            ]
    if cfont == 'Times':
        latex_lines.append(r'\usepackage{txfontsb}')
    latex_lines += [
            r'\newcolumntype{m}{D{+}{\,\pm\,}{-1}}',
            r'\sisetup{separate-uncertainty = true}',
            r'\begin{document}',
            r'    \begin{table}[t]',
            r'        \caption{\label{your_label_here}Results}',
            r'        \begin{ruledtabular}',
            r'            \renewcommand{\arraystretch}{1.4}',
            r'            \begin{tabular}{c c D..{-1} m m}',
            ]
    texfile.write('\n'.join(latex_lines))
    texfile.write('\n')
    return texfile

def table_headings(texfile, levels=None):
    levels = levels or [1, 2]
    texlevels = [
            r'\multicolumn{1}{c}{$' + str(level) + r'\sigma$ C.L.}'
            for level in levels
            ]
    texfile.write(
            '    &    '.join([
                r'                Parameter',
                r'Prior',
                r'\multicolumn{1}{c}{Best-fit}',
                ] + texlevels
                )
            )
    texfile.write(r'    \\    \hline')
    texfile.write('\n')

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

def trapezoids(density, x=None):
    if x is None:
        x = np.arange(density.size)
    assert x.size == density.size
    return (density[:-1] + density[1:])/2 * np.diff(x)

def power_notation(unit):
    if len(str(unit)) > 3:
        return r'10^{' + str(int(np.log10(unit))) + r'}'
    else:
        return str(unit)

def append_distribution_parameters_to_tex(texfile, tex, bf, sigmasCL, prior='', unit=1, fmt=5):
    unitstr = power_notation(unit) + r'\,' if unit != 1 else ''
    if hasattr(prior, 'mu'):
        priorstr = bool(prior) and r'$\mathcal{N}\left(' + ' ,'.join(["%.2f" % (unit*prior.mu), "%.2f" % (unit*prior.sigma)]) + r'\right)$' or prior
    else:
        priorstr = bool(prior) and r'$\left[' + ' ,'.join(["%.2f" % (unit*prior.vmin), "%.2f" % (unit*prior.vmax)]) + r'\right]$' or prior
    texfile.write(
            '\t&\t'.join([
                r'                $' + unitstr + tex.replace('mathrm','text') + '$',
                priorstr,
                (unit*bf).__format__(".%if" % fmt),
                ] + sigmasCL
                ) + '\t' + r'\\' + '\n'
            )
    return None

def close_tex(texfile):
    texfile.write(
            '\n'.join([
                r'            \end{tabular}',
                r'        \end{ruledtabular}',
                r'    \end{table}',
                r'\end{document}',
                ])
            )
    texfile.write('\n')
    texfile.close()
    return None

def resample(sample, size):
    if sample.size < size:
        import multiprocessing
        support, density = make_kde([sample,],)
        cpu = multiprocessing.cpu_count()
        size = size - sample.size
        manager = multiprocessing.Manager()
        slices = manager.list(range(cpu))
        if size % cpu == 0:
            jobs = [multiprocessing.Process(
                target = resample_job,
                args = (support, density, size//cpu, i, slices)
                ) for i in range(cpu)]
        else:
            jobs = [multiprocessing.Process(
                target = resample_job,
                args = (support, density, size//(cpu-1), i, slices)
                ) for i in range(cpu-1)]
            if size % (cpu - 1) > 0:
                jobs.append(multiprocessing.Process(
                    target = resample_job,
                    args = (support, density, size % (cpu-1), cpu - 1, slices)
                    ))
        for j in jobs:
            j.start()
        for j in jobs:
            j.join()
        newsample = np.concatenate([sample, np.concatenate([sl for sl in slices if type(sl) is np.ndarray])])
        np.random.shuffle(newsample)
        assert newsample.size == size + sample.size
        return newsample
    else:
        return sample[:size]


def resample_job(support, density, size, i, slices):
    np.random.seed()
    uniform = st.distributions.uniform(0, 1).rvs(size)
    newsample = []
    for u in uniform:
        F = interp1d(support, [integrate.trapz(
            density[:j+1], x=support[:j+1]) - u for j in range(len(support))])
        q = bisect(F, support[0], support[-1])
        newsample.append(q)
    slices[i] = np.array(newsample)
    return np.array(newsample)

def LogNormalMode(mu, sigma):
    return np.exp(mu - sigma**2)

def LogNormalPDF(x, mu, sigma):
    return 1/x/sigma/np.sqrt(2*np.pi) * np.exp(-1/2*(np.log(x)-mu)**2/sigma**2)

def LogNormalCDF(x, mu, sigma):
    return 1/2 + 1/2 * erf((np.log(x)-mu)/np.sqrt(2)/sigma)

def NormalPDF(x, mu, sigma):
    return 1/np.sqrt(2*np.pi)/sigma * np.exp(-1/2*(x-mu)**2/sigma**2)

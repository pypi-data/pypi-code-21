from __future__ import division 
import numpy as np
from scipy.optimize import curve_fit

def exponential_corr(x, tau):
    return np.exp(-x/tau)

def fit_tau(time, listcorr, P):
    popt, _ = curve_fit(exponential_corr, xdata=time, ydata=listcorr, p0=P)
    return popt[0]

#def fit_multipeak_gaussians(X, H):
#    popt, _ = curve_fit(two_peak_gaussian, xdata=X, ydata=H)
#    return popt

#def two_peak_gaussian(x, mu1, sigma1, w1, mu2, sigma2, w2):
#    return w1 * st.distributions.norm(mu1, sigma1).pdf(x) + \
#            w2 * st.distributions.norm(mu2, sigma2).pdf(x)

def draw_ellipse(InvFisher, means, CLsigma=1, precision=200):
    import scipy.stats as st
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

def uniform(u, v):
    return 1/(v-u)

def trapezoids(density, x=None):
    if x is None:
        x = np.arange(density.size)
    assert x.size == density.size
    return (density[:-1] + density[1:])/2 * np.diff(x)

def normalize(h, origlims, newlims=(0, 1)):
    P1, P2 = newlims
    H1, H2 = origlims
    return (h - H1)/(H2 - H1) * (P2 - P1) + P1

def symmetrize(x, x1, x2=None):
    if x2:
        return uncertainties.ufloat(x+0.8*(x1-x2), (x1+x2)/2) 
    else:
        # can't just return the same as above because would give x1/2
        return uncertainties.ufloat(x, x1)


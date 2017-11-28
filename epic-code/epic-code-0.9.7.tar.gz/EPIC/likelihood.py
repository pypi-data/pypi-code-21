from __future__ import division
#import matplotlib
#matplotlib.use('Agg')
#import matplotlib.pyplot as plt
from EPIC import common, hobservables
#import pdb
import uncertainties
import numpy as np
import scipy.stats as st
import scipy.interpolate as interpolate
import collections

class Cosmology(object):
    def __init__(self, params, fixed, model, log10Ai=-5, size=30000):
        self.model = model
        self.params = params
        self.fixed = fixed

        if 'darkSU2' in self.model:
            self.rk_densities = hobservables.integrate_densities(self,
                    log10Ai=log10Ai, size=size)
            if 'wnu0' in self.model:
                A, rho_Gamma, rho_phi0, rho_c = self.rk_densities 
                H = [hobservables.Hubble(a, np.array([rhoGamma, phi0, cdm]), self) \
                        for a, rhoGamma, phi0, cdm in zip(A, rho_Gamma,
                            rho_phi0, rho_c)]
            else:
                A, rho_Gamma, rho_phi0, rho_psi, rho_nu = self.rk_densities 
                H = [hobservables.Hubble(a, np.array([rhoGamma, phi0, psi, nu]), self) \
                        for a, rhoGamma, phi0, psi, nu in zip(A, rho_Gamma,
                        rho_phi0, rho_psi, rho_nu)]
            self.H_solution = interpolate.interp1d(common.z_of_a(A),
                    np.array(H))

        elif self.model == 'LIclusters_wd':
            self.rk_DE = hobservables.integrate_rhod_wcons(self,
                    log10Ai=-0.5, size=size)
            A, rho_d = self.rk_DE
            H = [hobservables.Hubble_LIclusters(a, d, self) for a, d in zip(A, rho_d)]
            self.H_solution = interpolate.interp1d(common.z_of_a(A), np.array(H))

def simple(datapoints, function, cosmology):
    samplesize = len(datapoints) 
    for data in datapoints:
        data.predicted = function(data.point, cosmology)
        if np.isnan(data.predicted):
            return -np.inf
        chi2 = (data.obs - data.predicted)**2 / data.sigma**2
        data.loglikelihood = - np.log(data.sigma) - chi2/2.
    total_likelihood = sum([data.loglikelihood for data in datapoints]) 
    total_likelihood += - samplesize/2 * common.log2pi
    return total_likelihood

def multipoints(datapoints, cosmology, function):
    samplesize = len(datapoints)
    chi2 = sum([(data.obs - pred)**2/data.sigma**2 for pred, data in zip(function(cosmology), datapoints)])
    if np.isnan(chi2):
        return -np.inf
    loglikelihood = - samplesize/2 * common.log2pi - sum([data.sigma for data in datapoints]) - chi2/2 
    return loglikelihood
    
def matrixform(datapoints, observ, predict):
    X = observ - predict
    try:
        chi2 = np.dot( np.dot(X.transpose(), datapoints.ICOV), X )
        return - datapoints.sample_size/2 * common.log2pi + 1/2 * datapoints.logdetICov - chi2/2
    except AttributeError:
        chi2 = np.dot( np.dot(X.transpose(), np.linalg.inv(datapoints.COV)), X )
        #return - chi2/2
        return - datapoints.sample_size/2 * common.log2pi - 1/2 * datapoints.logdetCov - chi2/2
    # the combined likelihood is the product of all the likelihoods, so the combined loglikelihood is the sum of the loglikelihoods

def matrixform_nuisance(sample_size, observ, predict, COV, logdetCov):
    X = observ - predict
    try:
        chi2 = float( X.T * COV.I * X )
    except ValueError:
        return -np.inf
    return - sample_size/2 * common.log2pi - 1/2 * logdetCov - chi2/2

###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################

def shift_parameters(datapoints, cosmology):
    dobs = datapoints.dist_obs.transpose()
    dpredict = datapoints.function(cosmology).transpose()
    return matrixform(datapoints, dobs, dpredict)

def clusters_virial_ratio(datapoints, cosmology):
    #for cl in datapoints:
    #    cl.Hubble(cosmology)
    #if np.any(np.isnan([cl.Hz for cl in datapoints])):
    #    return -np.inf
    ovr = [cl.ovr for cl in datapoints]
    #for i, OVR in enumerate(ovr):
    #    print(i, OVR)
    #ovr = np.array([(-3/2 * 1/1e14/GmumH) * (cl.r200 * cl.kTX * cl.fc/cl.M200) for cl in datapoints])
    xi = common.if_not_given(cosmology.params, cosmology.fixed, 'xi', 0.)
    dlnrhoH = [cl.dlnrhoH2(cosmology) for cl in datapoints]
    #if np.any(np.isnan([dln.nominal_value for dln in dlnrhoH])):
    #    return -np.inf
    DfE = [(- 1/(2+3*xi)) * num for num in dlnrhoH]
    #fig, ax = plt.subplots(4, 5)
    #fig.set_size_inches(5 * 3, 4 * 2.8)
    #DFEcopy = list(DfE)
    ##print(DFEcopy)
    #for num, cl, i in zip(DFEcopy, datapoints, range(len(datapoints))):
    #    jx, jy = divmod(i, 5)
    #    num = num[~np.isnan(num)]
    #    #num = num[abs(num/num.mean() - 1) < 0.1]
    ##    sup, kde = common.make_kde([num,])
    #    ax[jx][jy].hist(num, bins=30, normed=True, alpha=0.3)
    #    ax[jx][jy].set_yticklabels('')
    #    ax[jx][jy].tick_params(left='off', right='off')
    #    #x = np.linspace(num.min(), num.max(), 100)
    ##    ax[jx][jy].plot(sup, kde, lw=0.5, color='b', label=cl.name)
    ##    ax[jx][jy].legend()
    #fig.tight_layout()
    #fig.savefig('debug_DfE.pdf')
    obs_tvr = [OVR-DFE for OVR, DFE in zip(ovr, DfE)]
    #original_size = np.array([num.size for num in obs_tvr])
    obs_tvr = [num[~np.isnan(num)] for num in obs_tvr]
    #obs_tvr = [num[num < 1] for num in obs_tvr]
    #obs_tvr = [num[num > -3] for num in obs_tvr]
    #new_size = np.array([num.size for num in obs_tvr])
    #if np.any(new_size < 0.5 * original_size):
    #    #print(new_size, cosmology.params)
    #fig, ax = plt.subplots(4, 5)
    #fig.set_size_inches(5 * 2, 4 * 1.6)
    #for num, cl, i in zip(obs_tvr, datapoints, range(len(datapoints))):
    #    jx, jy = divmod(i, 5)
    #    print(cl.name)
    #    #sup, kde = common.make_kde([num,], thin=5)
    #    ax[jx][jy].hist(num, bins=40, normed=True, alpha=0.6, label=cl.name)
    #    #x = np.linspace(num.min(), num.max(), 100)
    #    #ax[jx][jy].plot(sup, kde, lw=0.5, color='b', label=cl.name)
    #    ax[jx][jy].legend()
    #fig.tight_layout()
    #fig.savefig('debug_OVR-DfE.pdf')
    #    return -np.inf

    #nom_tvr = np.array([tvr.nominal_value for tvr in obs_tvr])
    #nom_tvr = np.matrix(nom_tvr).T
    predict_tvr = hobservables.th_virial_ratio(cosmology) * np.ones(len(datapoints))
    #predict_tvr = np.matrix(predict_tvr).T
    ##stddev_tvr = np.diag(np.array([tvr.std_dev for tvr in obs_tvr]))
    #stddev_tvr = uncertainties.covariance_matrix(obs_tvr)
    #CovMatrix = np.matrix(stddev_tvr)
    #logdetCov = np.linalg.slogdet(CovMatrix)[1]

    return np.sum([np.log(float(common.make_kde([num,], x=predict, thin=1)[1])) for num, predict in zip(obs_tvr, predict_tvr)])
    #return np.sum([np.log(float(interp_pdf(predict))) for interp_pdf, predict in zip(obs_tvr, predict_tvr)])
    #return matrixform_nuisance(len(datapoints), nom_tvr, predict_tvr, CovMatrix, logdetCov)
    
def sym_clusters_virial_ratio(datapoints, cosmology):
    ovr = [cl.ovr for cl in datapoints]
    xi = common.if_not_given(cosmology.params, cosmology.fixed, 'xi', 0.)
    dlnrhoH = [cl.dlnrhoH2(cosmology) for cl in datapoints]
    DfE = [(- 1/(2+3*xi)) * num for num in dlnrhoH]
    obs_tvr = [OVR-DFE for OVR, DFE in zip(ovr, DfE)]
    predict_tvr = hobservables.th_virial_ratio(cosmology) * np.ones(len(datapoints))

    return np.sum([np.log(1/tvr.std_dev * common.scipy_stats_standard_normal.pdf((predict-tvr.nominal_value)/tvr.std_dev)) for tvr, predict in zip(obs_tvr, predict_tvr)])

def JLA_binned_data(datapoints, cosmology):
    mupredict = hobservables.muthsimple(datapoints.z, cosmology).transpose()
    if np.any(np.isnan(mupredict)):
        return -np.inf
    muobs = datapoints.muB.transpose()
    Mpar = common.if_not_given(cosmology.params, cosmology.fixed, 'M', 0.0)
    M = (Mpar *np.ones(datapoints.sample_size)).transpose()
    return matrixform(datapoints, muobs, M + mupredict)

def JLA_full_SNe_data(datapoints, cosmology):
    mupredict = np.matrix(hobservables.muth(datapoints, cosmology)).T
    if np.any(np.isnan(mupredict)):
        return -np.inf
    alpha = common.if_not_given(cosmology.params, cosmology.fixed, 'alpha', 0.14)
    beta = common.if_not_given(cosmology.params, cosmology.fixed, 'beta', 3.1)
    A = np.matrix(datapoints.matrixA(alpha, beta)) 
    MBpar = common.if_not_given(cosmology.params, cosmology.fixed, 'MBpar', -19.02)
    deltaMB = common.if_not_given(cosmology.params, cosmology.fixed, 'deltaMB', -0.06)
    MB = np.matrix(datapoints.MB(MBpar, deltaMB)).T
    muobs = A * datapoints.eta - MB
    CovMatrix = datapoints.COV(A)
    logdetCov = np.linalg.slogdet(CovMatrix)[1]
    return matrixform_nuisance(datapoints.sample_size, muobs, mupredict, CovMatrix, logdetCov)

def BAO_ratio(datapoints, cosmology):
    return simple(datapoints, hobservables.rBAO, cosmology)

def cosmicchrono(datapoints, cosmology):
    return simple(datapoints, hobservables.H, cosmology)

def f_sigma8(datapoints, cosmology):
    return simple(datapoints, hobservables.myfsigma8, cosmology)

def disttest(datapoints, cosmology):
    X = list(cosmology.params.values())
    LL = np.log(st.distributions.norm(0.5, 0.01).pdf(X[0])) +\
            np.log(st.distributions.norm(0.2, 0.03).pdf(X[1])) +\
            np.log(0.7*st.distributions.norm(0.3, 0.02).pdf(X[2]) + 0.3*st.distributions.norm(0.75, 0.02).pdf(X[2]))
    return LL

def compute_logposterior(datapoints, params, fixed, priors, model, beta=1.):
    LogPrior = common.logpriordist(params, priors)
    if np.isinf(LogPrior) or np.isnan(LogPrior):
        return -np.inf, -np.inf
    else:
        cosmology = Cosmology(params, fixed, model)
        totalloglikelihood = sum([allprobes[key](datapoints[key], cosmology) for key in datapoints.keys()])

        if np.isnan(totalloglikelihood):
            return -np.inf, -np.inf
        else:
            logpost = beta * totalloglikelihood + LogPrior # except for a constant, this is the Bayes theorem
            return logpost, totalloglikelihood

#===================================
# probes dictionary specifying which function must be used for each observable

allprobes = {
        'JLAsimple':    JLA_binned_data,
        'SNeJLA':       JLA_full_SNe_data,
        'Planck2015_distances':     shift_parameters,
        'CMB_WMAP7_shift':          shift_parameters,
        'clusters':     clusters_virial_ratio,
        'symclusters':     sym_clusters_virial_ratio,
        'BAO':          BAO_ratio,
        'fs8':          f_sigma8,
        'CosmicChrono': cosmicchrono,
        'disttest': disttest,
        'lognormal_parameters': shift_parameters,
        }


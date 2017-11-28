from __future__ import division
from __future__ import print_function
#import matplotlib
#matplotlib.use('Agg')
#import matplotlib.pyplot as plt
import numpy as np
from EPIC import common
from EPIC.hobservables import CMBdistances, PlanckDistancePriors, H, a, lognormal_parameters_function
import os
import pyfits
import glob
import collections
import uncertainties
import scipy.stats as st

class JLAsimple_dataset(object):
    def __init__(self, Cov, z, mu):
        self.COV = Cov
        self.ICOV = np.linalg.inv(self.COV)
        self.logdetICov = np.linalg.slogdet(self.ICOV)[1]
        self.logdetCov = - self.logdetICov
        self.z = z
        self.muB = mu
        self.sample_size = self.z.size

class Planckshift(object):
    def __init__(self, distobs, Cov):
        self.COV = Cov
        self.ICOV = np.linalg.inv(self.COV)
        self.logdetICov = np.linalg.slogdet(self.ICOV)[1]
        self.logdetCov = - self.logdetICov
        self.dist_obs = distobs
        self.sample_size = self.dist_obs.size
        self.function = PlanckDistancePriors

class CMBshift(object):
    def __init__(self, distobs, ICov):
        self.ICOV = ICov
        self.logdetICov = np.linalg.slogdet(self.ICOV)[1]
        self.dist_obs = distobs
        self.sample_size = self.dist_obs.size
        self.function = CMBdistances

class Covs(object):
    def __init__(self, z_mu, log10MB, eta, Ceta, A012, diagcov):
    #def __init__(self, z_mu, x1color, CovD, CovC, Ceta, A012, diagcov):
        self.zCMB, self.zHEL = z_mu
        self.log10MB = log10MB

        self.sample_size = self.log10MB.size
        self.eta = np.matrix(eta).T
        self.Ceta = np.matrix(Ceta)
        self.A0, self.A1, self.A2 = A012
        self.scoh, self.slens, self.sz = diagcov

    def MB(self, MBpar, deltaMB):
        simpleMB = [MBpar + deltaMB * (logM > 10) for logM in self.log10MB]
        return np.array(simpleMB)

    def matrixA(self, alpha, beta):
        return self.A0 + alpha * self.A1 - beta * self.A2

    def COV(self, A):
        C = A * self.Ceta * A.T 
        sig2z = np.matrix(np.diag(5 * 150e3/common.speedoflight / self.sz / common.ln10)**2)
        sig2lens = np.matrix(np.diag(self.slens)**2)
        sig2coh = np.matrix(np.diag(self.scoh)**2)
        C += sig2z + sig2lens + sig2coh
        #Dstat = self.sigma2_mBi + alpha**2 * self.sigma2_X1i + beta**2 * self.sigma2_Ci + 2*alpha*self.C_mBX1i - 2*beta*self.C_mBCi - 2*alpha*beta*self.C_X1Ci
        #Cstatsys = self.V0 + alpha**2 * self.Va + beta**2 * self.Vb + 2*alpha*self.V0a - 2*beta*self.V0b -2*alpha*beta*self.Vab
        return C
        
class Measurement(object):
    def __init__(self, data):
        self.point = data[0]
        self.obs = data[1]
        self.sigma = data[2]

class PlanckMeasurement(object):
    def __init__(self, data):
        self.obs = data[0]
        self.sigma = data[1]

class Cluster(object):
    def __init__(self, cl, wdir):
        self.name = cl
        with open(os.path.join(wdir, '%s.nfw.z' % self.name), 'r') as f:
            self.z = float(f.readline().strip())
        self.M200 = np.loadtxt(os.path.join(wdir, 'M200', '%s.M200' % self.name))
        self.r200 = np.loadtxt(os.path.join(wdir, 'r200', '%s.r200' % self.name))
        self.c =    np.loadtxt(os.path.join(wdir, 'c200', '%s.c200' % self.name))
        self.kTX =  np.loadtxt(os.path.join(wdir, 'kTX', '%s.kTX' % self.name))
        self.fc, self.dFdc = common.fc_gc_dFdc_from_c(self.c)
        self.ovr = self.r200 * self.kTX * self.fc / self.M200
        self.ovr = self.ovr * (-3/2 * 1e-14/common.GmumH)
        common.pasta(wdir, 'OVR')
        np.savetxt(os.path.join(wdir, 'OVR', '%s.OVR' % self.name), self.ovr)
        print('        %s loaded.' % self.name)

    def Hubble(self, cosmology):
        h = common.if_not_given(cosmology.params, cosmology.fixed, 'h', 0.7)
        #Hparams = dict(params)
        #Hparams['Obh2'] = 0
        #Hparams['Orh2'] = 0
        #self.Hz = H(self.z, Hparams, fixed, 'wCDM')/h #in units of h km/s/Mpc
        #'LIclusters' or 'lcdm' 
        Hz = H(self.z, cosmology)/h # in units of h km/s/Mpc
        return Hz

    #def M_r(self, var, mass_or_radius, h_data=0.72, Och2=0.27, Delta=200):
    #    data_cosmology = {
    #            'h':    h_data,
    #            'Och2': Och2 * h_data**2,
    #            'Obh2':     0.0,
    #            'Orh2':     0.0,
    #            }
    #    Hz = self.Hubble(data_cosmology, {}, 'lcdm')
    #    if not hasattr(self, 'rhoc'):
    #        self.rhoc = common.rho_critical(Hz)

    #    if var == 'r': 
    #        factor = (1/(4*np.pi/3)/Delta/self.rhoc)**(1/3) * (1e14)**(1/3)
    #        r200 = mass_or_radius**(1/3) * factor
    #        return r200
    #    elif var == 'M': 
    #        factor = Delta * 4/3 * np.pi * self.rhoc
    #        M = factor * mass_or_radius**3 
    #        return M
    #    else:
    #        raise

    #def dlnrhoH(self, params):
    #    xi = common.if_not_given(params, fixed, 'xi', 0)
    #    dlnrhow = (self.c * self.gc - 3)/self.r200
    #    sigX = (self.kTX/common.mumH)**(1/2)
    #    vth = (self.M200 / self.fc / self.r200)**(1/2) * (2/3 *(1+3*xi)/(2+3*xi) * common.G * 1e14)**(1/2)
    #    rdot = sigX - vth
    #    res = dlnrhow * rdot
    #    return res/self.Hz #  adimensional!

    def dlnrhoH2(self, cosmology):
        self.Hz = self.Hubble(cosmology)
        self.rhoc = common.rho_critical(self.Hz)
        #Gprime = 300 * self.rhoc / common.mumH  # this is Msun Mpc^-3 / keV (km/2)^-2
        #Gprime *= 1.2115534045e52  # this in units of Mpc^-3
        ## so the term Gprime * self.kTX will have units of keV Mpc^-3 (energy density)
        Gprime_over_F = self.fc / self.r200**2
        Gprime_over_F *= 1 / self.rhoc * (- 9)/(8*np.pi) /200 / common.GmumH # 1/keV
        dlnF_times_r200 = 2 - self.dFdc/self.fc * self.c # this product is adimensional
        res = (3 * Gprime_over_F * self.kTX + dlnF_times_r200)

        g = common.if_not_given(cosmology.params, cosmology.fixed, 'gamma', 0.5)
        res *= (g**2 * 3**(g+1))**(1/(1-g))
        res /= self.Hz
        #np.savetxt("res_%s.txt" % self.name, res)
        #return common.MixedDist(*common.fit_asymmetrical(res))
        return res

    def __repr__(self):
        return self.name

class SymCluster(Cluster):
    def __init__(self, cl, wdir, Mmu, Msig, cmu, csig, Tmu, Tsig):
        self.name = cl
        with open(os.path.join(wdir, '%s.nfw.z' % self.name), 'r') as f:
            self.z = float(f.readline().strip())
        self.M200 = uncertainties.ufloat(Mmu, Msig)
        self.c = uncertainties.ufloat(cmu, csig)
        self.kTX = uncertainties.ufloat(Tmu, Tsig)
        Om = 0.27
        Ode = 1 - Om
        Hz = 100 * np.sqrt(Om*(1+self.z)**3 + Ode)
        rhoc = 3 * Hz**2 / 8 / np.pi / common.G
        self.r200 = (3 / (4*np.pi) / 200 / rhoc)**(1/3) * (1e4)**(1/3) * self.M200**(1/3)
        self.fc, self.dFdc = common.fc_gc_dFdc_from_c(self.c)
        self.ovr = self.r200 * self.kTX * self.fc / self.M200
        self.ovr = self.ovr * (-3/2 * 1e-14/common.GmumH)
        common.pasta(wdir, 'OVR')
        with open(os.path.join(wdir, 'OVR', 'symclusters.OVR'), 'a') as f:
            f.write('\t'.join([self.name, str(self.ovr)]) + '\n')
        print('        %s loaded.' % self.name)

def JLAsimple(obsble):
    print('    Reading simplified JLA dataset...')
    print('        %s' % obsble)
    z, muB = np.loadtxt(os.path.join(obsble, 'data', 'jla_mub.txt'), unpack=True)
    Cov = np.loadtxt(os.path.join(obsble, 'data', 'jla_mub_covmatrix.dat'), skiprows=1).reshape([z.size,z.size])
    dataset = JLAsimple_dataset(Cov, z, muB)
    return 'JLA', dataset.sample_size, dataset

def Planck2015_distances(obsble):
    print('    Reading distance priors from Planck 2015...')
    print('        %s' % obsble)
    dist_obs, sigmas = np.loadtxt(os.path.join(obsble, 'CMBdistances.txt'), unpack=True)
    Corr = np.loadtxt(os.path.join(obsble, 'corr.txt')).reshape([dist_obs.size, dist_obs.size])
    Cov = common.corr_to_cov(sigmas, Corr)
    dataset = Planckshift(dist_obs, Cov)
    return 'Planck2015', dataset.sample_size, dataset

def CMB_WMAP7_shift(obsble):
    print('    Reading CMB shifts data from WMAP7...')
    print('        %s' % obsble)
    dist_obs = np.loadtxt(os.path.join(obsble, 'CMBdistances.txt'))
    ICov = np.loadtxt(os.path.join(obsble, 'invcov.txt')).reshape([3,3])
    dataset = CMBshift(dist_obs, ICov)
    return 'WMAP7', dataset.sample_size, dataset

def clusters(obsble):
    print('    Reading clusters virial ratio data...')
    print('        %s' % obsble)
    if obsble.endswith('.txt'):
        cluster_collection = common.readfile(obsble)
        obsble = cluster_collection.pop(0).strip()
        if cluster_collection[0].strip() == 'all':
            cluster_collection = os.listdir(obsble)
            #mudar
            cluster_collection = [cl[:-4] for cl in cluster_collection if cl.endswith('.nfw')]
        else:
            cluster_collection = [cl.strip() for cl in cluster_collection]
    else:
        cluster_collection = [obsble,]
        obsble = 'clusters_data'
    dataset = [Cluster(cl, obsble) for cl in cluster_collection]
    print('        Clusters ' + ', '.join([CL.name for CL in dataset]) + '.')
    return 'VR', len(dataset), dataset

def symclusters(obsble):
    print('    Reading clusters virial ratio data...')
    print('        %s' % obsble)
    if obsble.endswith('.txt'):
        cluster_collection = common.readfile(obsble)
        obsble = cluster_collection.pop(0).strip()
        if cluster_collection[0].strip() == 'all':
            cluster_collection = os.listdir(obsble)
            #mudar
            cluster_collection = [cl[:-4] for cl in cluster_collection if cl.endswith('.nfw')]
        else:
            cluster_collection = [cl.strip() for cl in cluster_collection]
    else:
        cluster_collection = [obsble,]
        obsble = 'clusters_data'
    with open(os.path.join(obsble, 'newclusters.vir'), 'r') as f:
        lines = f.readlines()
    newdata = {}
    for line in lines:
        splitted = line.strip().split()
        newdata[splitted[0]] = [float(value) for value in splitted[1:]]
    dataset = [SymCluster(cl, obsble, *newdata[cl]) for cl in cluster_collection]
    print('        Clusters ' + ', '.join([CL.name for CL in dataset]) + '.')
    return 'VR', len(dataset), dataset

def BAO(obsble):
    print('    Reading BAO (6dF+SDSS+BOSS+Lyalpha+WiggleZ) data...')
    print('        %s' % obsble)
    dataset = [Measurement(data) for data in np.loadtxt(obsble)]
    return 'BAO', len(dataset), dataset

def SNeJLA(obsble):
    print('    Reading SNeJLA data...')
    print('        %s' % obsble)
    zcmb, zhel, muB, x1, color, log10MB = np.loadtxt(os.path.join(obsble, 'data', 'jla_lcparams.txt'), unpack=True, usecols=(1, 2, 4, 6, 8, 10))
    Size = muB.size
    diagcov = np.loadtxt(os.path.join(obsble, 'covmat', 'sigma_mu.txt'), unpack = True)
    eta = np.zeros(3 * Size)
    distance_estimate = muB, x1, color
    for k in range(len(distance_estimate)):
        eta[k::3] = distance_estimate[k]
    C_eta = sum([pyfits.getdata(mat) for mat in glob.glob(os.path.join(obsble, 'covmat', 'C*.fits'))])
    A012 = [np.zeros((Size, 3*Size)) for k in range(3)]
    for i in range(Size):
        for k in range(3):
            A012[k][i,3*i+k] = 1.
    redshifts = zcmb, zhel
    dataset = Covs(redshifts, log10MB, eta, C_eta, A012, diagcov)
    return 'full JLA', dataset.sample_size, dataset

def fs8(obsble):
    print('    Reading fs8 data...')
    print('        %s' % obsble)
    dataset = [Measurement(data) for data in np.loadtxt(obsble)]
    return r'$f\sigma_8$', len(dataset), dataset

def CosmicChrono(obsble):
    print('    Reading cosmic chronometer H(z) data...')
    print('        %s' % obsble)
    dataset = [Measurement(data) for data in np.loadtxt(obsble)]
    return 'CC+$H_0$', len(dataset), dataset

def disttest(obsble):
    return 'disttest', 10, []

def lognormal_parameters(obsble):
    print('    Fitting asymmetrical errors with lognormal')
    print('        %s' % obsble)
    #Cov = np.diag(np.array([1e-2, 1e-2, 1e-2, 1e-4, 1e-4, 1e-4])**2)
    Cov = np.eye(3) * 1e-4**2
    obs = np.zeros(3)
    dataset = Planckshift(obs, Cov) 
    dataset.function = lognormal_parameters_function
    return 'asym errors fit', dataset.sample_size, dataset

def load_data(observables):
    datapoints = collections.OrderedDict()
    labels = []
    n_datapoints = 0
    for obs_name in observables.keys():
        tag, datasize, datapoints[obs_name] = eval('{0}(observables[\'{0}\'])'.format(obs_name))
        labels.append(tag)
        n_datapoints += datasize
    return n_datapoints, labels, datapoints


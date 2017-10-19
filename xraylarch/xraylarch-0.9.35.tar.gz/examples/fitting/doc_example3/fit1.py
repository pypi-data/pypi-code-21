import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

from lmfit import Parameters, minimize, report_fit

dat = np.loadtxt('unknown.dat')
s1 = np.loadtxt('s1.dat')
s2 = np.loadtxt('s2.dat')
s3 = np.loadtxt('s3.dat')
s4 = np.loadtxt('s4.dat')

# fit range, energy
emin, emax = 11870, 12030

imin = max(np.where(dat[:,0] <= emin)[0])
imax = max(np.where(dat[:,0] <= emax)[0])

data_en = dat[imin:imax+1, 0]
data_mu = dat[imin:imax+1, 1]

std1_mu = interp1d(s1[:,0], s1[:,1], kind='linear')(data_en)
std2_mu = interp1d(s2[:,0], s2[:,1], kind='linear')(data_en)
std3_mu = interp1d(s3[:,0], s3[:,1], kind='linear')(data_en)
std4_mu = interp1d(s4[:,0], s4[:,1], kind='linear')(data_en)


params = Parameters()
params.add('amp1', value=0.25, min=0, max=1)
params.add('amp2', value=0.25, min=0, max=1)
params.add('amp3', value=0.25, min=0, max=1)
params.add('amp4', expr='1 - amp1 - amp2 - amp3')

epsilon  = 0.001

def make_model(pars, std1_mu, std2_mu, std3_mu, std4_mu):
    a1 = pars['amp1'].value
    a2 = pars['amp2'].value
    a3 = pars['amp3'].value
    a4 = pars['amp4'].value

    return a1*std1_mu + a2*std2_mu + a3*std3_mu + a4*std4_mu 

def resid(pars, data_mu, std1_mu, std2_mu, std3_mu, std4_mu, epsilon):
    sum = make_model(pars, std1_mu, std2_mu, std3_mu, std4_mu)
    return (data_mu - sum)/epsilon

result = minimize(resid, params,
                  args=(data_mu, std1_mu, std2_mu, std3_mu, std4_mu, epsilon))

print report_fit(result)
init_fit = make_model(params, std1_mu, std2_mu, std3_mu, std4_mu)
best_fit = make_model(result.params, std1_mu, std2_mu, std3_mu, std4_mu)

plt.plot(data_en, data_mu, 'bo')
plt.plot(data_en, init_fit, 'r--')
plt.plot(data_en, best_fit, 'k-')

plt.show()

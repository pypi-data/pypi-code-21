"""
polyfit.py

author: Colin Clement
date: 2017-10-18

Minimal working example of using VariationalInference to fit polynomials
"""

import numpy as np
import varibayes.infer as infer
from varibayes.opt.adam import Adam

x = np.linspace(-1,1,100)
rng = np.random.RandomState(92089)

def loglikelihood(params, data, x=x):
    sigma = p[0]
    r = (np.polyval(params[1:], x) - data)/sigma
    return - np.sum(r*r + np.log(2*np.pi*sigma*sigma))/2.
    
def res(params, data, x=x):
    mod = np.polyval(params, x)
    return mod - data

if __name__=='__main__':
    import matplotlib.pyplot as plt
    # Make some interesting data
    zz = [-1, -0.4, 0, 0.4, 1.]
    pp = np.poly(zz)
    y = np.polyval(pp, x)
    ptp = y.ptp()
    y /= ptp

    sigma = 0.01  # we divide y by its ptp so sigma is 1/SNR
    p = np.hstack([sigma, pp])
    data = y + sigma*rng.randn(len(y))

    vb = infer.VariationalInferenceMF(loglikelihood, args=(data,),
                                      samples=30)

    p0 = np.hstack([sigma, 0*pp/ptp + 0.1*rng.randn(len(pp)),
                    0.1*rng.rand(len(p))])
    vb.fit(p0.copy(), iprint=100, tol=1E-8, itn=15000)

    opt = Adam(vb.evd_grad_evd_rao_blackwell)
    sol = opt.optimize(p0.copy(), iprint=100, tol=1E-8, itn=15000)
    plt.plot(vb.opt.obj_list, label='Adagrad')
    plt.plot(opt.obj_list, label='Adam')
    plt.legend()
    plt.show()

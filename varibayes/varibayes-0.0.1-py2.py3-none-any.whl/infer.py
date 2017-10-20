import numpy as np
import varibayes.opt.adadelta as adadelta


class VariationalInferenceMF(object):
    def __init__(self, loglikelihood, args=(), samples=12, **kwargs):
        self.loglikelihood = loglikelihood
        self.args = args
        self.params = []
        self.samples = samples
        self.opt = adadelta.Adadelta(self.evd_grad_evd_rao_blackwell, **kwargs)

    @property
    def mus(self):
        return self.params[:len(self.params)/2]

    @property
    def sigmas(self):
        return self.params[len(self.params)/2:]
    
    def sampledistn(self, n=None, params=None):
        params = params if params is not None else self.params
        mus, sigmas = params[:len(params)//2], params[len(params)//2:]
        return np.random.normal(mus, np.abs(sigmas), 
                                size=(n or self.samples, len(mus)))

    def logdistn(self, params=None, zs=None, n=None):
        zs = zs if zs is not None else self.sampledistn(n, params)
        params = params if params is not None else self.params
        m, s = params[:len(params)//2], params[len(params)//2:]
        r = (zs - m)/s
        return - np.sum(r*r + np.log(2*np.pi*s*s), axis=1)/2.

    def gradlogdistn(self, params=None, zs=None, n=None):
        zs = zs if zs is not None else self.sampledistn(n, params)
        params = params if params is not None else self.params
        mus, sigmas = params[:len(params)//2], params[len(params)//2:]
        r = (zs - mus)/sigmas
        return np.concatenate([r/sigmas, (r*r-1)/sigmas], 1)

    def evidence(self, params=None, zs=None, n=None):
        zs = zs if zs is not None else self.sampledistn(n, params)
        logl = np.array([self.loglikelihood(z, *self.args) for z in zs])
        return logl - self.logdistn(params, zs)
    
    def gradevidence(self, params=None, zs=None, n=None):
        zs = zs if zs is not None else self.sampledistn(n, params)
        evd = self.evidence(params, zs, n)
        grad = self.gradlogdistn(params, zs, n)
        return np.mean(grad * evd[:,None], axis=0)

    def evd_grad_evd(self, params, n=None):
        zs = self.sampledistn(n, params)
        evd = self.evidence(params, zs, n)
        grad = self.gradlogdistn(params, zs, n)
        return np.mean(evd), - np.mean(grad * evd[:,None], axis=0) 

    def evd_grad_evd_rao_blackwell(self, params, n=None):
        zs = self.sampledistn(n, params)
        evd = self.evidence(params, zs, n)
        grad = self.gradlogdistn(params, zs, n)

        grad_evd = grad * evd[:,None]
        mean_grad_evd = grad_evd.mean(0)
        mean_grad = grad.mean(0)
        a = np.mean((grad_evd-mean_grad_evd)*(grad-mean_grad),0)/grad.std(0)**2

        return np.mean(evd), - (mean_grad_evd - a * mean_grad)

    def fit(self, p0, **kwargs):
        self.params = self.opt.optimize(p0.copy(), **kwargs)

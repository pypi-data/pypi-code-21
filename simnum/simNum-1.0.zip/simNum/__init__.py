import numpy as np

def simDist(samples,distribution,mean=0,stddev=1,lamb=1,trials=None,probability=None):
    if distribution == 'normal':
        return np.random.normal(size=samples,loc=mean,scale=stddev)
    if distribution == 'poisson':
        return np.random.poisson(size=samples,lam=lamb)
    if distribution == 'binomial':
        if trials == None or probability == None:
            print('please include trials and probability arguments for binomial distribution')
        else:
            return np.random.binomial(size=samples,n=trials,p=probability)

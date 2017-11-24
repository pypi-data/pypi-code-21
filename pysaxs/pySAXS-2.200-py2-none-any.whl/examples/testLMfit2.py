from pySAXS.models import Gaussian
from pylab import *
from numpy import *
from scipy.optimize import curve_fit
from scipy import optimize


def GaussianFunction(x,p0,p1,p2,p3):
        """
        Gaussian model to fit the peak to get exact zero position
        p0 : height of gaussian
        p1 : is related to the FWHM
        p2 : center of gaussian
        p3 : background
        """
        print p0,p1,p2,p3
        sigm0=p1#*0.58870501125773733#((2*log(2))**0.5)/2
        return (p0-p3)*exp(-((x-p2)**2)/(p1*0.58)**2)+p3

def GaussianFunction2(pars, x):
        
        # unpack parameters:
        #  extract .value attribute for each parameter
        parvals = pars.valuesdict()
        p0 = parvals['p0']
        p1 = parvals['p1']
        p2 = parvals['p2']
        p3 = parvals['p3']
                
        """
        Gaussian model to fit the peak to get exact zero position
        p0 : height of gaussian
        p1 : is related to the FWHM
        p2 : center of gaussian
        p3 : background
        """
        print pars
        #p=list(args)
        #print args
        #if kwargs is not None:
        #    p+=sortedDictValues(kwargs)
        #print p
        '''p0=p[0]
        p1=p[1]
        p2=p[2]
        p3=p[3]'''
        print p0,p1,p2,p3
        sigm0=p1#*0.58870501125773733#((2*log(2))**0.5)/2
        return array((p0-p3)*exp(-((x-p2)**2)/(p1*0.58)**2)+p3)

def gaussian2(x, amp, wid,cen,bkg):
    #g=Gaussian()
    print [amp,wid,cen,bkg]
    return GaussianFunction(x,amp,wid,cen,bkg)
    
def gaussian(x, amp, wid,cen,bkg):
    print amp,cen,wid,bkg
    return (amp-bkg) * exp(-(x-cen)**2 /(wid*0.58)**2)+bkg

def sortedDictValues(adict):
    keys = adict.keys()
    keys.sort()
    return map(adict.get, keys)


#y2=ff(x,p0=5,p1=2,p2=3,p3=1)
x=arange(-10,10,0.1)
y=GaussianFunction(x,5,2,3,1)
plot(x,y,'b.')
popt, pcov = curve_fit(GaussianFunction, x, y,p0=[2,2,2,2])
#print popt
plot(x, GaussianFunction(x, popt[0], popt[1],popt[2],popt[3]), 'r-')

from lmfit import Model
from lmfit import Parameters, minimize, fit_report
#gmod = Model(ff)
#gmod=Model(gaussian2)
#result = gmod.fit(y, x=x, amp=2,wid=3,cen=1.0,bkg=1,method='nelder')
#result = gmod.fit(y, x=x, p0=2,p1=1,p2=1,p3=1,method='nelder')

#plot(x, result.init_fit, 'k--')
#plot(x, result.best_fit, 'r-')
#print result.best_values
fit_params = Parameters()
fit_params.add('p0', value=2)
fit_params.add('p1', value=2)
fit_params.add('p2', value=2)
fit_params.add('p3', value=2)

out = minimize(GaussianFunction2, fit_params, args=(x,), kws={'data':y})

print(fit_report(out))

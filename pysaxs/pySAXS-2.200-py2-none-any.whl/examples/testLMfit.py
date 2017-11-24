from pySAXS.models import Gaussian
from pylab import *
from numpy import *
from scipy.optimize import curve_fit

'''g=Gaussian()

g.q=x
g.Arg=[5,2,3,1]
y=g.getNoisy()'''
#plot(x,y,'b.')

'''


def gaussian(x, amp, wid,cen,bkg):
    g=Gaussian()
    g.q=x
    g.Arg=[amp,wid,cen,bkg]
    print g.Arg
    return g.getIntensity(x,[amp,wid,cen,bkg])'''
def GaussianFunction(x,**kwargs):
        """
        Gaussian model to fit the peak to get exact zero position
        p0 : height of gaussian
        p1 : is related to the FWHM
        p2 : center of gaussian
        p3 : background
        """
        
        #print args
        #♦p=list(args)
        print kwargs
        #if kwargs is not None:
        #    p+=sortedDictValues(kwargs)
        #print p
        p1=kwargs.get('p1')
        p2=kwargs.get('p2')
        p3=kwargs.get('p3')
        p0=kwargs.get('p0')
        print p0,p1,p2,p3
        sigm0=p1#*0.58870501125773733#((2*log(2))**0.5)/2
        return array((p0-p3)*exp(-((x-p2)**2)/(p1*0.5)**2)+p3)
    
def gaussian2(x, amp, wid,cen,bkg):
    #g=Gaussian()
    print [amp,wid,cen,bkg]
    return GaussianFunction(x,[amp,wid,cen,bkg])
    
def gaussian(x, amp, cen, wid,bkg):
    print amp,cen,wid,bkg
    return amp * exp(-(x-cen)**2 /wid)+bkg

def sortedDictValues(adict):
    keys = adict.keys()
    keys.sort()
    return map(adict.get, keys)

def ff(x,*args,**kwargs):
    #print args
    p=list(args)
    #print kwargs
    if kwargs is not None:
        p+=sortedDictValues(kwargs)
    print p
    g=Gaussian()
    '''g.Arg=p
    g.q=x'''
    r=g.getIntensity(q=x,arg=p)
    #print r
    return r 

#y2=ff(x,p0=5,p1=2,p2=3,p3=1)
x=arange(-10,10,0.1)
y=GaussianFunction(x,p0=5,p1=1,p2=1,p3=0)
plot(x,y,'b.')
from lmfit import Model
#gmod = Model(ff)
gmod=Model(GaussianFunction)
#result = gmod.fit(y, x=x, p0=5,p1=1,p2=1,p3=0.)
result = gmod.fit(y, x=x, p0=2,p1=2,p2=1,p3=1)
plot(x, result.init_fit, 'k--')
plot(x, result.best_fit, 'r-')
result=optimize.minimize(GaussianFunction,x0=1)
#print result.best_values
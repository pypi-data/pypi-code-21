from scipy import optimize
import numpy
from pylab import *
from lmfit import  Model

'''
test of fitting methods
http://stackoverflow.com/questions/14581358/getting-standard-errors-on-fitted-parameters-using-the-optimize-leastsq-method-i
by Pedro M Duarte
'''


def line( x, p):
    return p[0]*x + p[1] 

def linef( x, p0, p1):
    return p0*x + p1
    
def Gauss(x,p):
    h,w,f,b=p
    return Gaussf(x,h,w,f,b)
    
def Gaussf(q,h,w,f,b):
    sigm=f*((2*numpy.log(2))**0.5)/2
    return (h-b)*numpy.exp(-((q-w)**2)/sigm**2)+b

def fit_function(p0, datax, datay, function, **kwargs):

    errfunc = lambda p, x, y: function(x,p) - y

    ##################################################
    ## 1. COMPUTE THE FIT AND FIT ERRORS USING leastsq
    ##################################################

    # If using optimize.leastsq, the covariance returned is the 
    # reduced covariance or fractional covariance, as explained
    # here :
    # http://stackoverflow.com/questions/14854339/in-scipy-how-and-why-does-curve-fit-calculate-the-covariance-of-the-parameter-es
    # One can multiply it by the reduced chi squared, s_sq, as 
    # it is done in the more recenly implemented scipy.curve_fit
    # The errors in the parameters are then the square root of the 
    # diagonal elements.   
    pfit, pcov, infodict, errmsg, success = \
        optimize.leastsq( errfunc, p0, args=(datax, datay), \
                          full_output=1,diag=1/numpy.array(p0))

    if (len(datay) > len(p0)) and pcov is not None:
        s_sq = (errfunc(pfit, datax, datay)**2).sum()/(len(datay)-len(p0))
        pcov = pcov * s_sq
    else:
        pcov = inf

    error = [] 
    for i in range(len(pfit)):
        try:
          error.append( numpy.absolute(pcov[i][i])**0.5)
        except:
          error.append( 0.00 )
    pfit_leastsq = pfit
    perr_leastsq = numpy.array(error) 


    ###################################################
    ## 2. COMPUTE THE FIT AND FIT ERRORS USING curvefit
    ###################################################

    # When you have an error associated with each dataY point you can use 
    # scipy.curve_fit to give relative weights in the least-squares problem. 
    datayerrors = kwargs.get('datayerrors', None)
    curve_fit_function = kwargs.get('curve_fit_function', function)
    if datayerrors is None:
        pfit, pcov = \
            optimize.curve_fit(curve_fit_function,datax,datay,p0=p0)
    else:
        pfit, pcov = \
             optimize.curve_fit(curve_fit_function,datax,datay,p0=p0,\
                                sigma=datayerrors)
    error = [] 
    for i in range(len(pfit)):
        try:
          error.append( numpy.absolute(pcov[i][i])**0.5)
        except:
          error.append( 0.00 )
    pfit_curvefit = pfit
    perr_curvefit = numpy.array(error)  


    ####################################################
    ## 3. COMPUTE THE FIT AND FIT ERRORS USING bootstrap
    ####################################################        

    # An issue arises with scipy.curve_fit when errors in the y data points
    # are given.  Only the relative errors are used as weights, so the fit
    # parameter errors, determined from the covariance do not depended on the
    # magnitude of the errors in the individual data points.  This is clearly wrong. 
    # 
    # To circumvent this problem I have implemented a simple bootstraping 
    # routine that uses some Monte-Carlo to determine the errors in the fit
    # parameters.  This routines generates random datay points starting from
    # the given datay plus a random variation. 
    #
    # The random variation is determined from average standard deviation of y
    # points in the case where no errors in the y data points are avaiable.
    #
    # If errors in the y data points are available, then the random variation 
    # in each point is determined from its given error. 
    # 
    # A large number of random data sets are produced, each one of the is fitted
    # an in the end the variance of the large number of fit results is used as 
    # the error for the fit parameters. 

    # Estimate the confidence interval of the fitted parameter using
    # the bootstrap Monte-Carlo method
    # http://phe.rockefeller.edu/LogletLab/whitepaper/node17.html
    residuals = errfunc( pfit, datax, datay)
    s_res = numpy.std(residuals)
    ps = []
    # 100 random data sets are generated and fitted
    for i in range(100):
      if datayerrors is None:
          randomDelta = numpy.random.normal(0., s_res, len(datay))
          randomdataY = datay + randomDelta
      else:
          randomDelta =  numpy.array( [ \
                             numpy.random.normal(0., derr,1)[0] \
                             for derr in datayerrors ] ) 
          randomdataY = datay + randomDelta
      randomfit, randomcov = \
          optimize.leastsq( errfunc, p0, args=(datax, randomdataY),\
                            full_output=0)
      ps.append( randomfit ) 

    ps = numpy.array(ps)
    mean_pfit = numpy.mean(ps,0)
    Nsigma = 1. # 1sigma gets approximately the same as methods above
                # 1sigma corresponds to 68.3% confidence interval
                # 2sigma corresponds to 95.44% confidence interval
    err_pfit = Nsigma * numpy.std(ps,0) 

    pfit_bootstrap = mean_pfit
    perr_bootstrap = err_pfit


    ####################################################
    ## 4. COMPUTE THE FIT AND FIT ERRORS USING lmfit
    ####################################################   
    

    

    # Print results 
    print "\nlestsq method :"
    print "pfit = ", pfit_leastsq
    print "perr = ", perr_leastsq
    print "\ncurvefit method :"
    print "pfit = ", pfit_curvefit
    print "perr = ", perr_curvefit
    print "\nbootstrap method :"
    print "pfit = ", pfit_bootstrap
    print "perr = ", perr_bootstrap
    return pfit_leastsq,pfit_curvefit,pfit_bootstrap
    
# Lets look at how the methods defined above work for some simple linear data
# First look at the case when no errors are available for the y data points,
# for the data we will add a random spread with std_dev = 1.0

data_spread =0.5

# Generate random data 
datax = np.linspace( 0., 10, 100)
datay0 = Gauss( datax, [10,4 ,3,0.5 ]) 
datay = datay0 + numpy.random.normal(0., data_spread, len(datay0))

#plot(datax, datay0,'.')
plot(datax, datay,'.',label='raw data')
pINIT=[5,2 ,1,0.1 ]
a,b,c=fit_function(pINIT , datax, datay, Gauss, curve_fit_function=Gaussf) 
plot(datax,Gauss(datax,a),label='leastsq')
plot(datax,Gauss(datax,b),label='pfit_curvefit')
#plot(datax,Gauss(datax,c),label='bootstrap')
#lmfit
gmod = Model(Gaussf)
h,w,f,b=pINIT
result = gmod.fit(datay,q=datax, h=h,w=w,f=f,b=b)
print(result.fit_report())

legend()



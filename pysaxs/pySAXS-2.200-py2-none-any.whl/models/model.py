# -*- coding: cp1252 -*-
"""
LIONS_SAXS python routines for small angle xray scattering.
Model class
version 0.1b 04/07/2010
04-07-2010 DC: calculation of residuals corrected in fitBounds
04-07-2010 DC: calculation of chi square corrected
03-07-2010 DC: syntax error on fitBounds corrected
"""


import sys
from string import *
from math import *
#import Numeric
import numpy
from scipy import special as SPspecial
from scipy import stats as SPstats
from scipy import integrate as SPintegrate
from scipy import optimize 
from scipy.optimize import curve_fit
import random
from time import clock
from xml.etree import ElementTree
from pySAXS.tools import xmltools
import pySAXS
from lmfit import minimize, Minimizer, Parameters, Parameter, report_fit

class Model:
    '''
    Model class templates
    test
    '''
    IntensityFunc=None #function
    N=0
    q=None          #q range(x scale)
    Arg=[]        #list of parameters values
    ArgBound=[]   #list of parameters bounds [(0.0,10.0),(1.1,2.2)]
    Format=[]     #list of c format
    istofit=[]    #list of boolean for fitting
    name=""         #name of the model can be different from the class name
    Doc=[]          #list of description for parameters
    Description=""  # description of model
    Author="LIONS"  #name of Author
    WarningForCalculationTime=False     #if calculation time is too high, set to false
    specific=False  #for specific model, set to true
    prefit=None     #prefit function, by default is None
    res=None        #result parameter for the fit
    err=[]
    '''
    def prefit(self,Iexp):
        #   try to estimate some parameters from Iexp
        #return a list of estimate parameters
        
        return [1,2,3,4,5,6]
    '''
    
    def __init__(self,q=None,Arg=[],istofit=None,name=""):
        #print "class model init"
        self.Arg=[]
        self.Format=[]
        self.ArgBound=[]
        self.istofit=[]
        self.err=[] #uncertainties on the parameter
        if q<>None:
            self.q=q
        if (Arg<>[])and (Arg!=None):
            self.Arg=Arg
        if name!="":
            self.name=name
        #if istofit == none then fit all datas (array of true)
        if (istofit==None)and (self.istofit==None):
            self.istofit=Arg
            if len(Arg)>=0:
                for i in range(len(Arg)):
                    self.istofit[i]=True
        
    
    def __str__(self):
        return "Model "+self.name+ " with parameters : "+str(self.Arg)
        
    def __repr__(self):
        return self.__str__()
    
    def xml(self):
        '''
        return an xml object
        with name, args, and isTofit
        <model name='Gaussian'>
        <par value='0.123' fit='true'>height of gaussian</par>
        ...
        </model>
        '''
        #create the root </root><root>
        root_element = ElementTree.Element("model",name=self.__class__.__name__)
        for i in range(len(self.Arg)):
            attrib={'value':str(self.Arg[i]),\
                    'fit':str(self.istofit[i]),
                    'order':"%02i"%(i)}#str(i)}
            child = ElementTree.Element("par",attrib)
            child.text=str(self.Doc[i])
            #now append
            root_element.append(child)
        return root_element
        
    
    def addParameter(self,description,value,istofit=True,dataformat='%6.2f',bound=None):
        self.Arg.append(value)
        self.Doc.append(description)
        self.istofit.append(istofit)
        self.Format.append(dataformat)
        self.ArgBound.append(bound)


    def getNumber(self):
        return self.N
    def setQ(self,q):
        '''
        set the q scale
        '''
        self.q=q
        
    def getQ(self):
        '''
        get the q scale
        as a numpy array
        '''
        temp=numpy.zeros(len(self.q),dtype='float')
        for i in range(len(self.q)):
            temp[i]=self.q[i]
        return temp
    
    def setArg(self,par):
        '''
        set the model parameters
        '''
        self.Arg=par
        
    def getArg(self):
        '''
        return the model parameters 
        as list
        '''
        temp=list(range(len(self.Arg)))
        for i in range(len(self.Arg)):
            temp[i]=self.Arg[i]
        return temp
    
    def getArgBounds(self):
        temp=[]
        #print self.ArgBound
        for i in range(len(self.Arg)):
            #print i
            if  i>len(self.ArgBound)-1:
                temp.append(None)
            else:
                temp.append(self.ArgBound[i])
        #print temp        
        return temp

    def setIstofit(self,ITF):
        '''
        set istofit varaiable
        '''
        self.istofit=ITF
        
    def getIstofit(self):
        temp=list(range(len(self.istofit)))
        for i in range(len(self.istofit)):
            temp[i]=self.istofit[i]
        return temp

    def getIntensity(self,q=None,arg=None):
        '''
        compute the intensity function for the model
        '''
        if q is not None:
            self.q=q
        if arg is not None:
            self.Arg=arg
            
        #try:
        y=self.IntensityFunc(self.q,self.Arg)
        #except:
        #y=numpy.zeros(numpy.shape(self.q))
        return y
    
    def getNoisy(self,randompercent=0.1):
        '''
        return a noisy intensity computed for the model
        '''
        y=self.getIntensity()
        for i in range(len(self.q)):
            y[i]=y[i]*(1+((random.random()-0.5)*randompercent))
        return y
    
    def getBoundsFromParam(self,aroundParam=0.2):
        '''
        return bounds of parameters
        with a percent of aroundParam
        '''
        bounds=[]
        for i in range(len(self.Arg)):
            boundsmin=self.Arg[i]*(1-aroundParam)
            boundsmax=self.Arg[i]*(1+aroundParam)
            bounds.append((boundsmin,boundsmax))
        return bounds
            
    def residuals(self,par,Iexp,plotexp=0):
        """
        residuals
        par is the list of the parameters to be fitted
        """
        par_to_fit=numpy.array(self.Arg[:])
        j=0 
        for i in range(len(par_to_fit)):
            if self.istofit[i]==True:
                par_to_fit[i]=float(par[j])
                j+=1
        #print 'par to fit : ',par_to_fit
        if plotexp==5:
            err=(numpy.log(Iexp)-numpy.log(self.IntensityFunc(self.q,par_to_fit)))
        else:
            err=(Iexp*self.q**plotexp-self.IntensityFunc(self.q,par_to_fit)*self.q**plotexp)
        return err
    
    

    def residuals_bounds(self,par,Iexp,plotexp=0):
        """
        residuals used for the fit with bounds (arguments for leastsq and fmin.tnc are different)
        par is the list of the parameters to be fitted
        """
        par_to_fit=self.Arg[:]
        j=0 
        for i in range(len(par_to_fit)):
            if self.istofit[i]==True:
                par_to_fit[i]=par[j]
                j+=1
        #print 'par_to_fit',par_to_fit
        err=numpy.sum((Iexp*self.q**plotexp-self.IntensityFunc(self.q,par_to_fit)*self.q**plotexp)**2)
        return err
        
    def chi_carre(self,par,Iexp,plotexp=0):
        '''
        chi_carre
        par is the list of all parameters (either to be fitted or not)
        Here the chi square is calculated assuming that the standard deviation equals the function
        '''
        '''par=[]
        for i in range(len(self.Arg)):
            if self.istofit[i]==True:
                par.append(self.Arg[i])
        '''
        res=self.residuals(par,Iexp,plotexp)**2.
        i=self.IntensityFunc(self.q,par)
        chi = numpy.sum(res/i)
        return chi
    
    def fit(self,Iexp,plotexp=0,verbose=False):
        '''
        Fit the models with leastsq
        '''
        # params can be not fitted (from istofit)
        #--produce a new param : param0
        print "-----FIT  PYSAXS -------------"
        #print Iexp
        param0=[]
        self.err=[]
        NF=0 #if many parameters to fit
        for i in range(len(self.Arg)):
            if self.istofit[i]:
                param0.append(self.Arg[i])
                NF=NF+1
            self.err.append(None)
        #print param0
        #print self.Arg
        #-- fitting procedure
        #param0=abs(numpy.array(param0))
        t0=clock()
        res=optimize.leastsq(self.residuals,param0,args=(Iexp,plotexp),\
                             full_output=1,diag=1/abs(numpy.array(param0)))
        t1=clock()
        if verbose:
            print 'Parameters found for the fit= ', res[0], ' in ',t1-t0,'s'  
            #print 'Covariance matrix of the parameters',res[1]
            #print res
            #print 'res.ier : ',res.ier
            #print info,mesg,ier
        # results to new params
        par=self.Arg
        self.res=res
        j=0
        for i in range(len(par)):
            if self.istofit[i]:
                if NF==1:
                    par[i]=res[0]
                else:
                    par[i]=res[0][j]
                #par[i]=res[j]
                j=j+1
        
        pfit, pcov, infodict, errmsg, success=res
        if verbose:
            print errmsg
        '''if pcov is not None:
            sq=self.chi_carre(par, Iexp,plotexp)
            print 'chi-carre:',sq
            s_sq1=(self.residuals(pfit,self.q,plotexp)**2).sum()/(len(self.q)-len(pfit))
            s_sq = (infodict['fvec']**2).sum()/ (len(self.q)-len(pfit))
            print 's_sq\t',s_sq,'\ts_sq**plotexp',s_sq**plotexp,'\ts_sq1\t',s_sq1
            pcov0=pcov*(s_sq**plotexp)
            error0=[]
            pcov1=pcov*s_sq1
            error1=[]
            for i in range(len(pfit)):
                error0.append(numpy.absolute(pcov0[i][i])**0.5)
                error1.append(numpy.absolute(pcov1[i][i])**0.5)
            print par
            print error0
            print error1'''
        return par
    
        '''
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
                              full_output=1)
    
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
        '''
    
    
    def fitBounds(self,Iexp,bounds,plotexp=0,verbose=False):
        '''
        fit the model with fmin_tnc 
        with bounds as 
        bounds = [(0.0,10.0)]
        bounds must have same size than params
        '''
        # params can be not fitted (from istofit)
        #--produce a new param : param0
        # and newbounds
        #if isttofit is not True, then bounds or params are not taken into acount
        param0=[]
        newbounds=[]
        NF=0
        for i in range(len(self.Arg)):
            if self.istofit[i]==True:
                param0.append(self.Arg[i])
                newbounds.append(bounds[i])
                NF=NF+1
        #fitting with bounds
        t0=clock()
        res, nfeval, rc = optimize.fmin_tnc(self.residuals_bounds, param0, fprime=None, args=([Iexp,plotexp]),\
                                  approx_grad=1, bounds=newbounds, epsilon=1e-08, scale=None, messages=0,\
                                  maxCGit=-1, maxfun=None, eta=-1, stepmx=0, accuracy=0, fmin=0, ftol=-1, rescale=-1)
        t1=clock()
        if verbose:
            print 'Parameters found for the fit= ', res, ' in ',t1-t0,'s'  
        # results to new params
        par=self.Arg
        j=0
        for i in range(len(par)):
            if self.istofit[i]==True:
                if NF==1:
                    par[i]=res
                else:
                    par[i]=res[j]
                #par[i]=res[j]
                j=j+1
        return par
        
        return message
    
    def fu2(self,*args):
        #print args
        x=args[0]
        par=args[1:]
        print par
        par_to_fit=numpy.array(self.Arg[:])
        j=0 
        for i in range(len(par_to_fit)):
            if self.istofit[i]==True:
                par_to_fit[i]=float(par[j])
                j+=1
        return self.IntensityFunc(x,par_to_fit)
    
    def cfit(self,Iexp,plotexp=0,verbose=False):
        '''
        using curve fit
        '''
        param0=[]
        self.err=[]
        NF=0 #if many parameters to fit
        for i in range(len(self.Arg)):
            if self.istofit[i]:
                param0.append(self.Arg[i])
                NF=NF+1
            self.err.append(None)
        #print param0
        #print self.Arg
        #-- fitting procedure
        #param0=abs(numpy.array(param0))
        t0=clock()
        '''
        fit
        '''
        popt, pcov = curve_fit(self.fu2, self.q, Iexp,p0=param0)
        print popt
        #self.popt=popt
        #plt.plot(X2,Y2, 'b-')
        #plt.grid()
        #print "Best Radius :",popt[2], "nm  Sigma : ",popt[1]
        
        t1=clock()
        if verbose:
            print 'Parameters found for the fit= ', res, ' in ',t1-t0,'s'  
            
        # results to new params
        par=self.Arg
        res=popt
        j=0
        for i in range(len(par)):
            if self.istofit[i]:
                if NF==1:
                    par[i]=res
                else:
                    par[i]=res[j]
                #par[i]=res[j]
                j=j+1
        
        #pfit, pcov, infodict, errmsg, success=res
        #if verbose:
        #    print errmsg
        return par
    
    
    def residualLMFIT(self,par,x,data,plotexp=0):
        """ model decaying sine wave, subtract data"""
        #v = params.valuesdict()
        ppar=[]
        for i in par:
            ppar.append(par[i])
        #print plotexp,"  " ,ppar
        #err=(Iexp*self.q**plotexp-self.IntensityFunc(self.q,par_to_fit)*self.q**plotexp)
        model = self.IntensityFunc(self.q,ppar)*self.q**plotexp
        return model - data*self.q**plotexp
    
    def fitLMFIT(self,Iexp,plotexp=0,verbose=False):
        params = Parameters()
        paramDict=[]
        for i in range(len(self.Arg)):
            params.add('p'+str(i),value=self.Arg[i],vary=self.istofit[i])
            paramDict.append('p'+str(i))
        # do fit, here with leastsq model
        #print plotexp
        minner = Minimizer(self.residualLMFIT, params, fcn_args=(self.q, Iexp,plotexp))
        result = minner.minimize()
        
        # calculate final result
        final = Iexp + result.residual
        
        # write error report
        report_fit(result)
        res=result.params.valuesdict()
        par=[]
        par_err=[]
        for i in range(len(self.Arg)):
            par.append(res[paramDict[i]])
            pp=result.params[paramDict[i]]
            #print pp, paramDict[i]
            #print pp.stderr,"   ",pp.value
            if pp.vary:
                par_err.append(pp.stderr)
            else:
                par_err.append(None)
            #self.Doc[i]+' %s +/-%6.2f %s' % (pp.value, pp.stderr, spercent)
            
        return par,par_err
    
    def _deepcopy(self):
        """
        return a deepcopy of the dataset object
        """
        from copy import  deepcopy
        return deepcopy(self)
    
def getModelFromXML(element):
    attrib=element.attrib
    #print attrib
    if not(attrib.has_key('name')):
           return None
    M=None
    modelname=attrib['name']
    #try:
    M=getattr(pySAXS.models,modelname)()#create a new model
    #print "create new model from class :",modelname
    arg={}
    istofit={}
    l=[]
    for subelement in element:
            tag=subelement.tag
            subattrib=subelement.attrib
            #print tag, subattrib
            if subattrib.has_key('order'):
                if subattrib.has_key('value'):
                    arg[int(subattrib['order'])]=float(subattrib['value'])
                    istofit[int(subattrib['order'])]=subattrib['fit']
                    l.append(int(subattrib['order']))
    #here we have a list and a dictionnary
    #print l
    l.sort()
    #print l
    returnArg=[]
    returnIsToFit=[]
    #print arg
    for i in l:
            i=int(i)
            returnArg.append(arg[i])
            returnIsToFit.append(xmltools.convertText(istofit[i],datatype='bool'))
    M.Arg=returnArg
    M.istofit=returnIsToFit
    #print M
    '''except :
        print 'problem when trying to create model ',modelname
    '''
    return M
        
                  

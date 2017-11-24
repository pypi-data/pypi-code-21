'''
project : pySAXS
description : class for subtracting background
authors : Olivier Tache

'''

#-------------------------------------------------

from numpy import *
from scipy import interpolate

def subtractFile(q,i,ierr,backfilename):
    '''
    subtract background from file name
    '''
    pass

def subtract2D(q,i,ierr=None,bq=None,bi=None,bierr=None,interpolation=True):
    '''
    subtract background from q,i,ierr
    q,i,ierr : q, i , error
    bq : background q
    bi : background i
    bierr : background error
    
    if ierr or bierr is none : no error calculation
    if interpolate is False : no interpolation
    if bq is none : no interpolation
    '''
    final_error=None
    if bq is None:
        interpolation=False
    if not(interpolation):#without interpolation
        
        if (bierr is not None) and (ierr is not None):
            final_error=ierr+bierr
        else:
            final_error=None
        return q,i-ierr,final_error
    #with interpolation
    newf=interpolate.interp1d(bq,bi,kind='linear',bounds_error=0) #interpolation for i
    final_i=i-newf(q) #subtraction
    
    if (bierr is not None) and (ierr is not None):
        newfierr=interpolate.interp1d(bq,bierr,kind='linear',bounds_error=0) #interpolation for i
        final_error=ierr+newfierr(q)
    return q,final_i,final_error

def subtract1D(q,i,ierr,value):
    '''
    subtract a background value
    '''
    return q,i-value,ierr


#!usr/bin/python

# Copyright 2016, Rohan Dandage <rraadd_8@hotmail.com,rohan@igib.in>
# This program is distributed under General Public License v. 3.  

"""
================================
``fit_curve``
================================
"""

import numpy as np
from scipy.optimize import curve_fit
import logging
logging.basicConfig(format='[%(asctime)s] %(levelname)s\tfrom %(filename)s in %(funcName)s(..): %(message)s',level=logging.DEBUG) # filename=cfg_xls_fh+'.log'


def fit_gauss(x, a, x0, sigma):
    """
    This fits gaussian.
    """
    return a*np.exp(-(x-x0)**2/(2*sigma**2))

def fit_gauss_params(data_vector): # x= pandas col eg. data_fit['FCS']
    """
    This function is used to calculate the mximum likelihood of Fitness of synonymous mutations (later used for normalization).
    
    :param data_vector: pandas column.
    """
    data_vector=data_vector.as_matrix() # make numpy array
    data_vector=data_vector[~np.isnan(data_vector)] # denan
    
    if len(data_vector)!=0 :
        if len(data_vector)<100:
            y, x_edges = np.histogram(data_vector,bins=np.ceil(np.log2(len(data_vector))) + 1) # stitch bins optimization strudige but freedman dicos is better
        elif len(data_vector)<200:
            y, x_edges = np.histogram(data_vector,bins=25) # stitch bins optimization strudige but freedman dicos is better
        else:
            y, x_edges = np.histogram(data_vector,bins=50) # stitch bins optimization strudige but freedman dicos is better
        x=(x_edges[:-1] + x_edges[1:])/2 #bin edges to bon centres
        popt,pcov = curve_fit(fit_gauss,x,y,p0=[1,data_vector.mean(),data_vector.std()])
        mean_gaus=popt[1]
        sdev_gaus=abs(popt[2])
        return (mean_gaus,sdev_gaus)
    else: 
        logging.info("data_vector=nans")    
        return False



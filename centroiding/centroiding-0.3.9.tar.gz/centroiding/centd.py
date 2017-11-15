# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 14:04:31 2017

@author:
Maximilian N. Guenther
Battcock Centre for Experimental Astrophysics,
Cavendish Laboratory,
JJ Thomson Avenue
Cambridge CB3 0HE
Email: mg719@cam.ac.uk
"""



from identify.centroiding import centroid
from identify.centroiding_multi import evaluate_candidate_shortlist



###############################################################################
# Define version
###############################################################################
__version__ = '0.3.9'



def identify(fieldname, obj_id, ngts_version, **kwargs):
    '''
    identify centroid shift for a given NGTS object via identify/centroiding.py.
    see identify/centroiding.py for docstring
    '''
    
    C = centroid(fieldname, obj_id, ngts_version, **kwargs) 
    C.run()



def identify_list(fname, **kwargs):
    '''
    identify centroid shifts for a list of objects
    
    Parameters
    ----------
    fname : string
        path and name of file which includes four columns:
        fieldname   obj_id  ngts_version    source
    dt : float
        precision in phase-folded time series; standard is 0.005
    outdir : str
        path to directory for output; 
        if None a folder called 'output' will be created in the current directory
    mode : str
        'skipfiles': any existing outputs in outdir will be skipped, judging by 'flagfile.txt'
        'newdir': a new outdir will be created with suffix _2
        'replacefiles': any existing outputs will be replaced with new ones
        
    Returns
    -------
    -
    '''
    
    evaluate_candidate_shortlist(fname, **kwargs)



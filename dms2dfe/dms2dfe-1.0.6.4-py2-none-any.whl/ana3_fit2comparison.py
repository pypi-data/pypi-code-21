#!usr/bin/python

# Copyright 2016, Rohan Dandage <rraadd_8@hotmail.com,rohan@igib.in>
# This program is distributed under General Public License v. 3.  

import sys
import os
from os.path import splitext, exists,basename, isdir,abspath,dirname
from Bio import SeqIO
from collections import Counter
import re
import numpy
import pandas as pd 
from scipy import optimize
from multiprocessing import Pool
data_cds_freq_fh="%s/lib/data_cds_freq.xls"% (abspath(dirname(__file__)))
import logging
logging.basicConfig(format='[%(asctime)s] %(levelname)s\tfrom %(filename)s in %(funcName)s(..): %(message)s',level=logging.DEBUG) # filename=cfg_xls_fh+'.log'
from dms2dfe import configure
from dms2dfe.lib.io_mut_files import data_fit2data_comparison,getusable_comparison_list
from dms2dfe.lib.global_vars import mut_types_form 
from dms2dfe.lib.io_mut_class import get_data_metrics

def main(prj_dh,test=False):
    """
    **--step 4**. Compares test (eg. treated) and control (eg. untreated) experiments.
    
    The output data is saved in `data_comparison` format as described in :ref:`io`.
    
    :param prj_dh: path to project directory.
    """
    logging.info("start")
    if not exists(prj_dh) :
        logging.error("Could not find '%s'" % prj_dh)
        sys.exit()
    configure.main(prj_dh)
    from dms2dfe.tmp import info
    cores=info.cores
    
    # SET global variables
    global prj_dh_global
    prj_dh_global=prj_dh
    if exists('%s/cfg/comparison' % prj_dh):
        comparison_pairs_list    =getusable_comparison_list(prj_dh)    
        if test:
            pooled_data_fit2data_comparison(comparison_pairs_list[0])
        else:
            pool=Pool(processes=int(cores)) 
            pool.map(pooled_data_fit2data_comparison,comparison_pairs_list)
            pool.close(); pool.join()
    else :
        logging.warning("do not exist: cfg/comparison")
    data_fit_metrics=get_data_metrics(prj_dh)
    logging.shutdown()

def pooled_data_fit2data_comparison(data_comparison_tp):
    """
    This converts the Fitness values to Relative fitness among test and control fed as input.

    :param data_comparison_tp: tuple with name (lbl) of control and test samples.
    """    
    lbl_ctrl=data_comparison_tp[0]
    lbl_test=data_comparison_tp[1]
    data_fit2data_comparison(lbl_ctrl,lbl_test,prj_dh_global)
    
if __name__ == '__main__':
    if len(sys.argv)==3:
        if sys.argv[2]=='test':
            test=True
        else:
            test=False
    else:
        test=False
    main(sys.argv[1],test=test)
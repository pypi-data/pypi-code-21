#!usr/bin/python

# Copyright 2016, Rohan Dandage <rraadd_8@hotmail.com,rohan@igib.in>
# This program is distributed under General Public License v. 3.  

import sys
import numpy as np
from os.path import exists,splitext
from os import makedirs
import pandas as pd
from multiprocessing import Pool
import logging
logging.basicConfig(format='[%(asctime)s] %(levelname)s\tfrom %(filename)s in %(funcName)s(..): %(message)s',level=logging.DEBUG) # filename=cfg_xls_fh+'.log'
from dms2dfe import configure
from dms2dfe.lib.io_mut_files import getusable_lbls_list,getusable_fits_list,mut_mat_cds2data_lbl,data_lbl2data_fit,data_lbl2data_fit_lite,transform_data_lbl,transform_data_lbl_deseq 

def main(prj_dh,test=False):
    """
    **--step 2**. Converts mutation matrices (.mat files produced in upstream ana1_sam2mutmat module) and calculates the fitness scores.
    
    The output data is saved in `data_fit` format as described in :ref:`io`.
    
    :param prj_dh: path to project directory.
    """
    logging.info("start")
    if not exists(prj_dh) :
        logging.error("Could not find '%s'" % prj_dh)
        sys.exit()
    configure.main(prj_dh)

    global prj_dh_global,host,norm_type,fsta_len,cctmr_global,output_dh,prj_dh_global,lbls,Ni_cutoff,fsta_fh_global,clips

    from dms2dfe.tmp import info
    fsta_fh=info.fsta_fh
    cctmr=info.cctmr
    host=info.host
    cores=info.cores
    transform_type=info.transform_type
    norm_type=info.norm_type
    fsta_len=info.fsta_len
    Ni_cutoff=int(info.Ni_cutoff)
    rscript_fh=info.rscript_fh
    if hasattr(info, 'mut_type'):
        mut_type=info.mut_type
    else:
        mut_type='single'    
    
    lbls=pd.read_csv(prj_dh+'/cfg/lbls')
    lbls=lbls.set_index('varname')

    # SET global variables
    prj_dh_global=prj_dh
    fsta_fh_global=fsta_fh    
    if cctmr != 'nan':
        cctmr=[int("%s" % i) for i in cctmr.split(" ")]
        cctmr_global=[(cctmr[0],cctmr[1]),(cctmr[2],cctmr[3])]
    else:
        cctmr_global=None

    if info.clips != 'nan':
        clips=[int(s) for s in info.clips.split(' ')]
    else:
        clips=None

    if mut_type=='single':
        lbls_list=getusable_lbls_list(prj_dh)
        if len(lbls_list)!=0:
            if test:
                pooled_mut_mat_cds2data_lbl(lbls_list[0])
            else:
                pool_mut_mat_cds2data_lbl=Pool(processes=int(cores)) 
                pool_mut_mat_cds2data_lbl.map(pooled_mut_mat_cds2data_lbl,lbls_list)
                pool_mut_mat_cds2data_lbl.close(); pool_mut_mat_cds2data_lbl.join()
        else:
            logging.info("already processed: mut_mat_cds2data_lbl")
        #TRANSFORM
        if (transform_type=='rlog') or (transform_type=='vst'):
            logging.info("transforming frequencies: %s" % transform_type)
            transform_data_lbl_deseq(prj_dh,transform_type,rscript_fh)
        else:
            logging.info("transforming frequencies: %s" % transform_type)
            transform_data_lbl(prj_dh,transform_type)
        #FITNESS
        fits_pairs_list=getusable_fits_list(prj_dh,data_fit_dh='data_fit')    
        if len(fits_pairs_list)!=0:
            if test:
                # pooled_data_lbl2data_fit(fits_pairs_list[0])      
                for fits_pairs in fits_pairs_list:
                    pooled_data_lbl2data_fit(fits_pairs)
            else:
                pool_data_lbl2data_fit=Pool(processes=int(cores)) 
                pool_data_lbl2data_fit.map(pooled_data_lbl2data_fit,
                                           fits_pairs_list)
                pool_data_lbl2data_fit.close(); pool_data_lbl2data_fit.join()
        else:
            logging.info("already processed: data_lbl2data_fit")
    elif mut_type=='double':
        fits_pairs_list_dm=getusable_fits_list(prj_dh,data_fit_dh='data_fit_dm')    
        if len(fits_pairs_list_dm)!=0:
            if test:
                data_lbl2data_fit_dm(fits_pairs_list_dm[0],prj_dh,data_lbl_dh='data_lbl_dm',
                        data_fit_dh='data_fit_dm')      
            else:
                for fits_pairs in fits_pairs_list_dm:
                    data_lbl2data_fit_lite(fits_pairs,prj_dh,data_lbl_dh='data_lbl_dm',
                        data_fit_dh='data_fit_dm')
        else:
            logging.info("already processed: data_lbl2data_fit")
    logging.shutdown()

def pooled_mut_mat_cds2data_lbl(lbls_list_tp):
    """
    This function converts mutation matrix (produced from .mat) file into data_lbl format.
    
    :param lbls_list_tp: tuple with name (lbl) of sample and path to file with codon level mutation matrix (.mat_mut_cds).
    """
    lbli=lbls_list_tp[0]
    lbl_mat_mut_cds_fh=lbls_list_tp[1]
    logging.info("processing : %s" % (lbli))
    mut_mat_cds2data_lbl(lbli,lbl_mat_mut_cds_fh,host,prj_dh_global,fsta_len,
                         cctmr_global,Ni_cutoff,fsta_fh_global,clips=clips)


def pooled_data_lbl2data_fit(fits_list):
    """
    This estimates Fitness (data_fit) from mutation data (data_lbl) in selcted and unselected samples.  

    :param fits_list: tuple with name (lbl) of input and selected samples.
    """
    from dms2dfe.tmp import info
    unsel_lbl=fits_list[0]
    sel_lbl=fits_list[1]
    logging.info("processing : %s and %s" % (unsel_lbl,sel_lbl))
    # try:
    data_lbl2data_fit(unsel_lbl,sel_lbl,info)
    # except:
    #     logging.error("check logs for %s and %s" % (unsel_lbl,sel_lbl))
        
if __name__ == '__main__':
    if len(sys.argv)==3:
        test=sys.argv[2]
    else:
        test=False
    main(sys.argv[1],test=test)
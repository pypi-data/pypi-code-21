#!usr/bin/python

# Copyright 2016, Rohan Dandage <rraadd_8@hotmail.com,rohan@igib.in>
# This program is distributed under General Public License v. 3.  

import sys
from os.path import exists,splitext
import logging
import numpy as np
import pandas as pd
from Bio.PDB import PDBParser
from Bio.PDB.Polypeptide import PPBuilder
from Bio import SeqIO
import logging
logging.basicConfig(format='[%(asctime)s] %(levelname)s\tfrom %(filename)s in %(funcName)s(..): %(message)s',level=logging.DEBUG) # filename=cfg_xls_fh+'.log'
from dms2dfe import configure
#from dms2dfe.lib.io_data_files import convert2h5form
from dms2dfe.lib.get_protein_features import get_data_feats_pos,get_data_feats_sub,get_data_feats_mut,get_data_feats_all
# getdssp_data,pdb2dfromactivesite,get_consrv_score,get_residue_depth

def main(prj_dh):
    """
    **--step 0.3**. Extracts molecular features of the gene.
    
    The out files are created in `prj_dh/data_feats`

    The steps and required dependendencies are following. 
    
    .. code-block:: text
    
        Secondary structure                      : using DSSP.
        Solvent Accessible Surface Area          : using DSSP.  
        Distance of a residue from reference atom: using Bio.PDB

    :param prj_dh: path to project directory.
    """
    logging.basicConfig(format='[%(asctime)s] %(levelname)s from %(funcName)s:\t%(message)s',level=logging.DEBUG) # filename=cfg_xls_fh+'.log'
    logging.info("start")

    if not exists(prj_dh) :
        logging.error("Could not find '%s'\n" % prj_dh)
        sys.exit()
    configure.main(prj_dh)
    from dms2dfe.tmp import info

    #FEATS PER POSITION
    data_feats_pos_fh="%s/data_feats/aas/data_feats_pos" % prj_dh
    data_feats_pos=get_data_feats_pos(prj_dh,info,data_out_fh=data_feats_pos_fh)
    #FEATS PER SUBSTITUTION
    data_feats_sub_fh="%s/data_feats/aas/data_feats_sub" % prj_dh
    data_feats_sub=get_data_feats_sub(data_out_fh=data_feats_sub_fh)
    #FEATS PER MUTATION
    data_feats_mut_fh="%s/data_feats/aas/data_feats_mut" % prj_dh
    data_feats_mut=get_data_feats_mut(prj_dh,data_feats_mut_fh,info)    
    #FEATS ALL
    data_feats_all_fh="%s/data_feats/aas/data_feats_all" % prj_dh
    data_feats_all=get_data_feats_all(data_feats_mut_fh,data_feats_pos_fh,data_feats_sub_fh,
                                     data_feats_all_fh,info)
    #back compatibility
    feats_all_fh="%s/data_feats/aas/feats_all" % prj_dh
    if not data_feats_pos is None:
        data_feats_pos.to_csv(feats_all_fh)
        
    logging.shutdown()

if __name__ == '__main__':
    main(sys.argv[1])
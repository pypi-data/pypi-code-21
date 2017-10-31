#!usr/bin/python

# Copyright 2016, Rohan Dandage <rraadd_8@hotmail.com,rohan@igb.in>
# This program is distributed under General Public License v. 3.  

import sys
from os.path import exists,splitext,basename,dirname
from os import makedirs
from glob import glob
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg') # no Xwindows
from multiprocessing import Pool
import warnings
warnings.simplefilter(action = "ignore", category = FutureWarning)
warnings.simplefilter(action = "ignore", category = DeprecationWarning)
# import logging
from dms2dfe.lib.io_strs import get_logger
logging=get_logger()
from dms2dfe import configure

def main(prj_dh,test=False,ml=False):
    """
    **--step 3**. Identifies molecular features that may determine fitness scores.
    
    This plots the results in following visualisations.
    
    .. code-block:: text
    
        ROC plots
        Relative importances of features
    
    :param prj_dh: path to project directory.
    """    
    logging.info("start")

    if not exists(prj_dh) :
        logging.error("Could not find '%s'" % prj_dh)
        sys.exit()
    configure.main(prj_dh)
    from dms2dfe.tmp import info


    from dms2dfe.tmp import info
    from dms2dfe.lib.io_ml import corrplot
    corrplot(info)

    if ml:
        from dms2dfe.lib.io_dfs import set_index
        from dms2dfe.lib.io_ml import data_fit2ml#,get_cols_del,make_data_combo,data_combo2ml
        cores=int(info.cores)
        if hasattr(info, 'mut_type'):
            mut_type=info.mut_type
        else:
            mut_type='single'    
        if hasattr(info, 'ml_input'):
            if info.ml_input=='FC':
                ml_input='FCA_norm'
            elif info.ml_input=='Fi':
                ml_input='FiA'
        else:
            ml_input='FCA_norm'    
        type_form="aas"
        if not exists("%s/plots/%s" % (prj_dh,type_form)):
            makedirs("%s/plots/%s" % (prj_dh,type_form))
        if not exists("%s/data_ml/%s" % (prj_dh,type_form)):
            makedirs("%s/data_ml/%s" % (prj_dh,type_form))
        data_feats=pd.read_csv("%s/data_feats/aas/data_feats_all" % (prj_dh))
            
        if mut_type=='single':
            data_fit_keys = ["data_fit/%s/%s" % (type_form,basename(fh)) \
                             for fh in glob("%s/data_fit/aas/*" % prj_dh) \
                             if (not "inferred" in basename(fh)) and ("_WRT_" in basename(fh))]
            data_fit_keys = np.unique(data_fit_keys)

            if len(data_fit_keys)!=0:
                if test:
                    pooled_io_ml(data_fit_keys[0])
                    # for data_fit_key in data_fit_keys:
                    #     pooled_io_ml(data_fit_key)
                else:
                    for data_fit_key in data_fit_keys:
                        pooled_io_ml(data_fit_key)
                    # pool_io_ml=Pool(processes=int(cores)) 
                    # pool_io_ml.map(pooled_io_ml,data_fit_keys)
                    # pool_io_ml.close(); pool_io_ml.join()
            else:
                logging.info("already processed")
        elif mut_type=='double':
            data_feats=set_index(data_feats,'mutids')
            data_fit_dh='data_fit_dm'
            data_fit_keys = ["%s/%s/%s" % (data_fit_dh,type_form,basename(fh)) \
                             for fh in glob("%s/%s/aas/*" % (prj_dh,data_fit_dh)) \
                             if (not "inferred" in basename(fh)) and ("_WRT_" in basename(fh))]
            data_fit_keys = np.unique(data_fit_keys)
            ycol=ml_input
            Xcols=data_feats.columns
            if len(data_fit_keys)!=0:
                for data_fit_key in data_fit_keys:
                    data_fit_dm_fh='%s/%s' % (prj_dh,data_fit_key)
                    data_combo_fh='%s/data_ml/aas/%s.combo' % (prj_dh,basename(data_fit_dm_fh))
                    force=False
                    if not exists(data_combo_fh) or force:
                        data_fit_dm=pd.read_csv(data_fit_dm_fh).set_index('mutids')
                        data_combo=make_data_combo(data_fit_dm,data_feats,ycol,Xcols)
                        if not exists(dirname(data_combo_fh)):
                            makedirs(dirname(data_combo_fh))
                        data_combo.to_csv(data_combo_fh)
                    else:
                        data_combo=pd.read_csv(data_combo_fh).set_index('mutids')
                    logging.info('ml: start')
                    data_combo2ml(data_combo,basename(data_fit_dm_fh),dirname(data_combo_fh),dirname(data_combo_fh),
                                ycoln=ycol,col_idx='mutids',ml_type='cls',
                                middle_percentile_skipped=0.1,force=False,)
    def pooled_io_ml(data_fit_key):
        """
        This module makes use of muti threading to speed up `dms2dfe.lib.io_ml.data_fit2ml`.     
        
        :param data_fit_key: in the form <data_fit>/<aas/cds>/<name of file>.
        """
        from dms2dfe.tmp import info
        dX_fh="%s/data_feats/aas/data_feats_all" % (info.prj_dh)
        dy_fh='%s/%s' % (info.prj_dh,data_fit_key)
        logging.info('processing: %s' % basename(dy_fh))
        data_fit2ml(dX_fh,dy_fh,info,regORcls='cls')
                    
    logging.shutdown()

    
if __name__ == '__main__':
    if len(sys.argv)==3:
        if sys.argv[2]=='test':
            test=True
        else:
            test=False
    else:
        test=False
    main(sys.argv[1],test=test)
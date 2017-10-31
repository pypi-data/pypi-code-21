#!usr/bin/python

# Copyright 2016, Rohan Dandage <rraadd_8@hotmail.com,rohan@igib.in>
# This program is distributed under General Public License v. 3.  

import sys
from os.path import exists,splitext,dirname
import argparse
import logging
from dms2dfe import configure, ana0_fastq2dplx,ana0_fastq2sbam,ana0_getfeats,ana1_sam2mutmat,ana2_mutmat2fit,ana3_fit2comparison,ana4_modeller,ana4_plotter
    
# GET INPTS    
def main():
    """
    This runs all analysis steps in tandem.

    From bash command line,

    .. code-block:: text

        python path/to/dms2dfe/pipeline.py path/to/project_directory
        
    :param prj_dh: path to project directory.
    
    Outputs are created in `prj_dh` in directories such as `data_lbl` , `data_fit` , `data_comparison` etc. as described in :ref:`io`.

    Optionally, In addition to envoking `pipeline`, individual programs can be accessed separately as described in :ref:`programs` section.
    Also submodules can be accessed though an API, as described in :ref:`api` section.
    Also the scripts can be envoked through bash from locally downloaded `dms2dfe` folder.

    """
    logging.info("start")
    parser = argparse.ArgumentParser(description='dms2dfe')
    parser.add_argument("prj_dh", help="path to project directory", 
                        action="store", default=False)    
    parser.add_argument("--test", help="Debug mode on", dest="test", 
                        action='store_true', default=False)    
    parser.add_argument("--step", help="0: configure project directory,\n0.1: demultiplex fastq by provided borcodes,\n0.2: alignment,\n0.3: get molecular features,\n1: variant calling,\n2: get preferential enrichments,\n3: identify molecular determinants,\n4: identify relative selection pressures,\n5: make visualizations", dest="step", 
                        type=float,action="store", choices=[0,0.1,0.2,0.3,1,2,3,4,5],default=None)  
    args = parser.parse_args()
    pipeline(args.prj_dh,test=args.test,step=args.step)

def pipeline(prj_dh,step=None,test=False):        
    if exists(prj_dh):
        if step==0 or step==None:
            configure.main(prj_dh,"deps")
            configure.main(prj_dh)          
        if step==0.1 or step==None:
            ana0_fastq2dplx.main(prj_dh)
        if step==0.2 or step==None:
            ana0_fastq2sbam.main(prj_dh,test)
        if step==0.3:
            ana0_getfeats.main(prj_dh)
        if step==1 or step==None:
            ana1_sam2mutmat.main(prj_dh)
        if step==2 or step==None:
            ana2_mutmat2fit.main(prj_dh,test)
        if step==3 or step==None:
            ana0_getfeats.main(prj_dh)
            ana4_modeller.main(prj_dh,test)
        if step==4 or step==None:
            ana3_fit2comparison.main(prj_dh,test)
        if step==5 or step==None:
            ana0_getfeats.main(prj_dh)
            ana4_plotter.main(prj_dh)
        if step==None:
            logging.info("Location of output data: %s/plots/aas/data_comparison" % (prj_dh))
            logging.info("Location of output visualizations: %s/plots/aas/" % (prj_dh))
            logging.info("For information about file formats of outputs, refer to http://kc-lab.github.io/dms2dfe/io .")
    else:
        configure.main(prj_dh)                  
    logging.shutdown()

if __name__ == '__main__':
    main()

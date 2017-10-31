#!usr/bin/python

# Copyright 2016, Rohan Dandage <rraadd_8@hotmail.com,rohan@igib.in>
# This program is distributed under General Public License v. 3.  

import sys
from os import makedirs,stat
from os.path import splitext, join, exists, isdir,basename,abspath,dirname
import pandas as pd 
from dms2dfe.lib.io_strs import get_logger
logging=get_logger()
from dms2dfe import configure
from dms2dfe.lib.io_plot_files import plot_coverage,plot_mutmap,plot_submap,plot_multisca,plot_pdb,plot_violin,plot_pies

def main(prj_dh):
    """
    **--step 5**. Generates vizualizations.

    #. Scatter grid plots raw counts in replicates, if present.
    #. Mutation matrix. of frequencies of mutants (log scaled). 
    #. Scatter plots of raw counts among selected and unselected samples 
    #. Mutation matrix. of Fitness values. 
    #. DFE plot. ie. Distribution of Fitness values for samples.
    #. Projections on PDB. Average of fitness values per residue are projected onto PDB file.  

    :param prj_dh: path to project directory.
    """
    logging.info("start")
    if not exists(prj_dh) :
        logging.error("Could not find '%s'" % prj_dh)
        sys.exit()
    configure.main(prj_dh)
    from dms2dfe.tmp import info
    for type_form in ['aas','cds']:
        plots_dh='%s/plots/%s' % (prj_dh,type_form)
        if not exists(plots_dh):
            makedirs(plots_dh)
        

    plot_coverage(info)
    plot_mutmap(info)
    plot_submap(info)
    plot_multisca(info)
    plot_pdb(info)
    plot_violin(info)
    # plot_pies(info)
    
if __name__ == '__main__':
    main(sys.argv[1])
#!usr/bin/python

# Copyright 2016, Rohan Dandage <rraadd_8@hotmail.com,rohan@igib.in>
# This program is distributed under General Public License v. 3.  

"""
================================
``ana0_plotter_pdb``
================================

This optional script use UCSF chimera libraries to produce projections of the fitness values onto PDB structure.

There are three key visualizations,

.. code-block:: text

    Front: 0 :sup:`0`
    Back : 180 :sup:`0` flip and
    Slice

Ligand would be colored green

Input/s : text file with list of paths to PDB files (with B-factor edited). 

"""

from os.path import abspath,dirname,exists,basename
import sys, getopt
from chimera import runCommand as rc
from chimera import replyobj
import logging
logging.basicConfig(format='[%(asctime)s] %(levelname)s\tfrom %(filename)s in %(funcName)s(..): %(message)s',level=logging.DEBUG) # 
with open('%s/../tmp/plot_pdb_chimera_fhs' % abspath(dirname(__file__)), 'r') as f:
    file_names = f.read().splitlines()
    
if not len(file_names)==0:
    for fn in file_names:
        if exists(fn):
            logging.info("processing %s" % basename(fn))
            replyobj.status("Processing " + fn)
            rc("open " + fn)
            rc("windowsize 800 800; align ligand ~ligand;\
               rangecol bfactor -0.5 blue 0 gray 0.5 red :.A;preset apply publication 2; \
                ~disp :.A,:.B;setattr m stickScale 2; delete :.B; delete solvent; delete :SPD; disp ligand;center :.A;\
                color gray,s; light mode ambient;color green ligand;\
                labelopt resinfo 'N-term'; rlabel protein & @n & @/idatmType=N3+;\
                labelopt resinfo 'C-term'; rlabel protein & @c &  @/idatmType=Cac; color black,l")
                # colorkey 0.85,0.3 0.88,0.7 0.5 red 0 gray 0.5 blue; \
                # 2dlabels create c%d text 'Fitness' xpos 0.81 ypos 0.25 color black;\" % file_names.index(fn) 
            
            rc("scale 1;")

            png_name = fn[:-3] + ".ps"
            rc("copy file %s supersample 3" % (fn[:-3] + "eps"))

            rc("turn y 180;")            
            rc("copy file %s supersample 3" % (fn[:-3] + "_180.eps"))

            rc("~rlabel;turn y 180;")            
            #  color white; ~ribbon; ~disp :.A,:.B;setattr m stickScale 2; delete :.B; delete solvent; delete :SPD; disp ligand;
            # color gray,s; light mode ambient; rangecol bfactor -2 blue 0 white 2 red :.A; color green ligand;
            rc("preset apply publication 1; rangecol bfactor -0.5 blue 0 gray 0.5 red :.A; surface probeRadius 0.05;\
                color green ligand\
               ")
                # labelopt resinfo 'N-term'; rlabel protein & @n & @/idatmType=N3+;\
                # labelopt resinfo 'C-term'; rlabel protein & @c &  @/idatmType=Cac; color black,l\

            rc("copy file %s supersample 3" % (fn[:-3] + "_surf_.eps"))

            rc("mclip #0 match focal; scolor #0 zone protein; light mode ambient;")
            rc("copy file %s supersample 3" % (fn[:-3] + "_surf_slice.eps"))

            rc("~mclip;turn y 180;")            
            rc("copy file %s supersample 3" % (fn[:-3] + "_surf_180.eps"))

            rc("mclip #0 match focal; scolor #0 zone protein; light mode ambient;")
            rc("copy file %s supersample 3" % (fn[:-3] + "_surf_slice_180.eps"))

            rc("close all")
        else:
            logging.info("can not find: %s" % basename(fn))
rc("stop now")



# windowsize 700 600; align ligand ~ligand;rangecol bfactor -0.5 blue 0 grey 0.5 red :.A;preset apply publication 2;~disp :.A,:.B;setattr m stickScale 2; delete :.B; delete solvent; delete :SPD; disp ligand; color gray,s; light mode ambient;color green ligand;colorkey 0.85,0.3 0.88,0.7 0.5 red 0 gray -0.5 blue; 2dlabels create c%d text 'Fitness' xpos 0.81 ypos 0.25 color black;

# rangecol bfactor -0.5 blue 0 white 0.5 red :.A; surface probeRadius 0.05;color green ligand;
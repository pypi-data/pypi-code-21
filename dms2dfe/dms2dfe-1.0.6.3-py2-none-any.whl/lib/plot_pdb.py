#!usr/bin/python

# Copyright 2016, Rohan Dandage <rraadd_8@hotmail.com,rohan@igib.in>
# This program is distributed under General Public License v. 3.  

"""
================================
``plot_pdb``
================================
"""
from Bio.PDB import PDBParser,PDBIO
from collections import Counter
import re
import pandas as pd 
from scipy import optimize
from multiprocessing import Pool
import numpy as np
import matplotlib 
import matplotlib.pyplot as plt
matplotlib.style.use('ggplot')
import seaborn as sns
import logging
logging.basicConfig(format='[%(asctime)s] %(levelname)s\tfrom %(filename)s in %(funcName)s(..): %(message)s',level=logging.DEBUG) # filename=cfg_xls_fh+'.log'


def vector2bfactor(vector,pdb_fh,pdb_clrd_fh):
    """
    Incorporates vector with values to the B-factor of PDB file.

    : param vector : vector with values
    : param pdb_fh : path of input PDB file
    : param pdb_clrd_fh : path of output PDB file 
    """
    aas_21_3letter=['ALA','ARG','ASN','ASP','CYS','GLN','GLU','GLY','HIS','ILE',
                    'LEU','LYS','MET','PHE','PRO','SER','THR','TRP','TYR','VAL']
    pdb_parser=PDBParser()
    pdb_data=pdb_parser.get_structure("pdb_name",pdb_fh)
    for model in pdb_data:
        for chain in model:
            for residue in chain:
                if residue.get_resname() in aas_21_3letter: #only aas 
                    for atom in residue:
                        #print residue.id[1]
                        # break
                        if residue.id[1]<=len(vector):
                            atom.set_bfactor(vector[residue.id[1]-1]) #residue.id is 1 based count 
    pdb_io = PDBIO()
    pdb_io.set_structure(pdb_data)
    pdb_io.save(pdb_clrd_fh) 



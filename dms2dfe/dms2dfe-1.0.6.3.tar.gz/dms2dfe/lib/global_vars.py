#!usr/bin/python

# Copyright 2016, Rohan Dandage <rraadd_8@hotmail.com,rohan@igib.in>
# This program is distributed under General Public License v. 3.  

"""
================================
``global_vars``
================================
"""
import numpy as np

aas_21_3letter=['ALA','ARG','ASN','ASP','CYS','GLN','GLU','GLY','HIS','ILE','LEU','LYS','MET','PHE','PRO','SER','THR','TRP','TYR','VAL']
aas_21=["A","C","D","E","F","G","H","I","K","L","M","N","P","Q","R","S","T","V","W","X","Y"] #for indexing
cds_64=["TTT",    "TTC",    "TTA",  "TTG",  "TCT",  "TCC",  "TCA",  "TCG",  "TAT",  "TAC",  "TAA",  "TAG",  "TGT",  "TGC",  "TGA",  "TGG",  "CTT",  "CTC",  "CTA",  "CTG",  "CCT",  "CCC",  "CCA",  "CCG",  "CAT",  "CAC",  "CAA",  "CAG",  "CGT",  "CGC",  "CGA",  "CGG",  "ATT",  "ATC",  "ATA",  "ATG",  "ACT",  "ACC",  "ACA",  "ACG",  "AAT",  "AAC",  "AAA",  "AAG",  "AGT",  "AGC",  "AGA",  "AGG",  "GTT",  "GTC",  "GTA",  "GTG",  "GCT",  "GCC",  "GCA",  "GCG",  "GAT",  "GAC",  "GAA",  "GAG",  "GGT",  "GGC",  "GGA",  "GGG"]
basecomplement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A' , 'N': 'N' } 
mut_types_form=['cds','aas']
mut_types_NorS=['N','S','A'] # N: nonsyn ,S:syn ,A: all N+S
secstruc_lbls=(["H","alpha helix"],
["B","beta bridge"],
["E","strand"],
["G","helix 3"],
["I","helix 5"],
["T","turn"],
["S","bend"],
["-",np.nan])    
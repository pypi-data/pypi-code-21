#!usr/bin/python

# Copyright 2016, Rohan Dandage <rraadd_8@hotmail.com,rohan@igib.in>
# This program is distributed under General Public License v. 3.  

"""
================================
``convert_seq``
================================
"""
from Bio.Seq import Seq
from Bio.Alphabet import generic_dna
import logging
logging.basicConfig(format='[%(asctime)s] %(levelname)s\tfrom %(filename)s in %(funcName)s(..): %(message)s',level=logging.DEBUG) # filename=cfg_xls_fh+'.log'

def cmplmt(s): 
	"""
	Gets complement of a sequence.
    
    :param s: sequence string.
	"""
	from dms2dfe.lib.global_vars import basecomplement

	letters = list(s) 
	letters = [basecomplement[base] for base in letters] 
	return ''.join(letters)
def revers(s):
	"""
	Gets reverse of a sequence.
    
    :param s: sequence string.
	"""
	return s[::-1]   
	 
def revcom(s):
	"""
	Gets reverse complement of a sequence.
    
    :param s: sequence string.
	"""
	return cmplmt(s[::-1])

def cds2aas(cds_str,host,stop_codon='X') :
    """
    This translates codons to amino acids.
    
    :param cds_str: codon sequence string.
    :param host: name of host organism for choosing codon table. [coli | yeast | sapiens].
    :returns aas: amino acid.
    """
    coding_dna = Seq(cds_str, generic_dna)
    #aas=''
    if len(coding_dna)%3 != 0 :
        # logging.error('len(coding_dna)%3 != 0')
        # print coding_dna
        return False
    elif "coli" in host :
            aas=str(coding_dna.translate(table=11)) # http://www.ncbi.nlm.nih.gov/Taxonomy/Utils/wprintgc.cgi
    elif "yeast" in host :
        aas=str(coding_dna.translate(table=12))
    elif "sapiens" in host :
        aas=str(coding_dna.translate(table=1))
    if stop_codon!='X':
        return aas
    else:
        return aas.replace("*", "X")


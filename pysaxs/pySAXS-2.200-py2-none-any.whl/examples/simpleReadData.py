import os
import pySAXS
from pySAXS.filefilters import fileimport
'''
an example on how to read data file 
'''
ff=fileimport.fileImport('txt')
q,i,err=ff.read(pySAXS.__path__[0]+os.sep+"saxsdata"+os.sep+"export-au.txt")

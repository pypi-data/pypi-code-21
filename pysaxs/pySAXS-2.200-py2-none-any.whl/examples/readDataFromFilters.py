import os
import pySAXS
from pySAXS.filefilters import fileimport
'''
an example on how to read data file with filter system
'''

#swing
print "swing"
f=pySAXS.__path__[0]+os.sep+"saxsdata"+os.sep+"datasample-swing.dat"
ff=fileimport.fileImport('swing')
q,i,err=ff.read(f)
print q,i,err

#txt
print "txt"
f=pySAXS.__path__[0]+os.sep+"saxsdata"+os.sep+"export-au.txt"
ff=fileimport.fileImport('txt')
q,i,err=ff.read(f)

#rgr
print "saxs rgr"
f=pySAXS.__path__[0]+os.sep+"saxsdata"+os.sep+"sample-lupolen-1800s.rgr"
ff=fileimport.fileImport('saxs')
q,i,err=ff.read(f)

#usaxs raw data
print "usaxs raw data"
f=pySAXS.__path__[0]+os.sep+"saxsdata"+os.sep+"datasample-usaxsRC.txt"
ff=fileimport.fileImport('usaxs')
q,i,err=ff.read(f)

#usaxs resolution function
print "usaxs res func"
f=pySAXS.__path__[0]+os.sep+"saxsdata"+os.sep+"usaxs_res_func.dat"
ff=fileimport.fileImport('resfunc')
q,i,err=ff.read(f)

#2 columns
print "2 columns"
f=pySAXS.__path__[0]+os.sep+"saxsdata"+os.sep+"datasample-2cols.txt"
ff=fileimport.fileImport('txt2c')
q,i,err=ff.read(f)

#2 columns with 3 columns plugin
print "2 columns with 3 columns plugin"
f=pySAXS.__path__[0]+os.sep+"saxsdata"+os.sep+"datasample-2cols.txt"
ff=fileimport.fileImport('txt')
q,i,err=ff.read(f)
print q,i,err

#fit2d
print "fit2d"
f=pySAXS.__path__[0]+os.sep+"saxsdata"+os.sep+"datasample-fit2d.chi"
ff=fileimport.fileImport('fit2d')
q,i,err=ff.read(f)

#comma sep
print "comma sep"
f=pySAXS.__path__[0]+os.sep+"saxsdata"+os.sep+"datasample-comma-sep.txt"
ff=fileimport.fileImport('txtcomma')
q,i,err=ff.read(f)
print q,i,err

#a new filter
print 'a new filter'
f=pySAXS.__path__[0]+os.sep+"saxsdata"+os.sep+"datasample-swing.dat"
ff=fileimport.fileImport(qcol=0,icol=1,errcol=2,skiprows=32)
ff.read(f)



#list of filters
print fileimport.import_list()
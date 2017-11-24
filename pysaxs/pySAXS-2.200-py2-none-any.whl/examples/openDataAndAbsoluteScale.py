'''
example of use for open a data file (rgr) and set in absolute scale
datas and parameter xml file are in saxsdata
#updated (08/2015)
'''
import numpy
import pySAXS
import os
from pySAXS.LS import SAXSparametersXML
from pySAXS.filefilters import fileimport
#get the filename
p=os.path.dirname(pySAXS.__file__)
dataFile="sample-lupolen-1800s.rgr"
completeDataFile=p+os.sep+"saxsdata"+os.sep+dataFile
#open data
q,i,error=fileimport.fileImport('saxs').read(completeDataFile)

'''
#old way to open file
completeData=numpy.loadtxt(completeDataFile)
data=completeData.transpose()
q=data[0]
i=data[1]
error=data[3]
'''

#get the parameter xml file
xmlfile="sample-lupolen-absolu.xml"
par=SAXSparametersXML.SAXSparameters()
par.openXML(p+os.sep+"saxsdata"+os.sep+xmlfile)
print par
#calculate all the parameters
par.calculate_All()
#calculate absolute intensities
iabs,errorabs=par.calculate_i(i,deviation=error)
#and plot...
import matplotlib.pyplot as plt
plt.plot(q,iabs,color='red')
plt.show()
'''
example of use for open a data file (rgr) and set in absolute scale
Without predefined absolute parameters
'''
import numpy
import pySAXS
import os
from pySAXS.LS import SAXSparametersXML
#get the filename
p=os.path.dirname(pySAXS.__file__)
dataFile="sample-lupolen-1800s.rgr"
completeDataFile=p+os.sep+"saxsdata"+os.sep+dataFile
#open data
completeData=numpy.loadtxt(completeDataFile)
data=completeData.transpose()
q=data[0]
i=data[1]
error=data[3]

#set the parameter xml file
par=SAXSparametersXML.SAXSparameters() #parameters are empty...
#parameters from the beamline setup
par.set('D',120.4)
par.set('K',5170000)
par.set('pixel_size', 0.015)
par.set('wavelength', 1.542)
par.set('backgd_by_s', 0.00062)
par.set('backgd_by_pix',14.55)
#parameters from the sample
par.set('thickness',0.3)
par.set('TransmittedFlux', 3.25)
par.set('IncidentFlux', 9.07)
par.set('time', 1800.0)

par.calculate_All()
iabs,errorabs=par.calculate_i(i,deviation=error)
#and plot...
import matplotlib.pyplot as plt
plt.plot(q,iabs,color='red')
plt.show()

'''
example of use for open a data file (rgr) and set in absolute scale
Without predefined absolute parameters
'''
import numpy
import pySAXS
import os
from pySAXS.LS import absolute
from pySAXS.tools import filetools
import matplotlib.pyplot as plt

#get the filename
p=os.path.dirname(pySAXS.__file__)
lupolen="g:\\test\\QB-2015-05-19-lupolen-3600s.rgr"
eau="Q://NIMBE//LIONS//SAXS//WAXS//2015//HG//HG-2015-05-19-eau-3600s.rgr"
vide="Q://NIMBE//LIONS//SAXS//WAXS//2015//HG//HG-2015-05-20-VIDE-3600s.rgr"
background="g:\\test\\QB-2015-05-19-background-3600s.TIFF.rgr"
solvent=""


solv=absolute.absolute(vide)#open data
solv.openRPT()#parameters from the beamline setup
solv.set('thickness',1)
solv.set('IncidentFlux', 1.7)
solv.set('K',24902166)
solv.subtractBackgroundFile(background)
solv.calculate()  

abs=absolute.absolute(eau) 
abs.openRPT()
abs.set('thickness',1)
abs.set('IncidentFlux', 1.7)
abs.set('K',24902166)
#print abs
abs.subtractBackgroundFile(background)
abs.calculate()

abs.subtractSolvent(solv.qAbs,solv.iAbs,solv.ierrAbs,vide,thickness=0.2)

abs.saveRPT()
abs.saveABS()

plt.plot(abs.q,abs.iAbs,color='red',label="eau")
plt.plot(solv.q,solv.iAbs,label="vide",color='blue')
plt.plot(abs.q,abs.iFinal,color='green')
plt.show()

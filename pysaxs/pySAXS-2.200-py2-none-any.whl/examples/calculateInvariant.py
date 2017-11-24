'''
example of importing data from a xml dataset 
and calculate invariant with different parameters
'''
import pySAXS
from pySAXS.guisaxs.dataset import *
from pySAXS.LS import invariant
import os
import numpy
#--- import datas from file
p=os.path.dirname(pySAXS.__file__)
dataFile="dataset_examples.xml"
completeDataFile=p+os.sep+"saxsdata"+os.sep+dataFile
dt=getDataDictFromXMLFile(completeDataFile)
q=dt['JBIV61_2500super/.173'].q
i=dt['JBIV61_2500super/.173'].i

#--- initialize invariant
invar=invariant.invariant(q,i,radius=30.0)
# parameters can be changed directly
invar.radius=30.0
#--- or in the calculate call
invar.calculate(radius=30.0)
invar.calculate(radius=100.0)
invar.calculate(qmax=0.184,extrapolation=0.92926904607e+28) #radius=100.0
vol=invar.getVolume()
#particule radius calculation
radius=((vol*3)/(4*numpy.pi))**(1.0/3)
print "particule radius = ",radius, " cm"

#--- plot
import matplotlib.pyplot as plt
plt.plot(q,i,color='red')
plt.plot(invar.LowQq,invar.LowQi,color='blue')
plt.plot(invar.HighQq,invar.HighQi,color='green')
plt.yscale('log')
plt.xscale('log')
plt.show()

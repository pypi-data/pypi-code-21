'''
example of use for open a data file (rgr) , plot, and fit
by a model
'''
import numpy
import pySAXS
import os
from matplotlib import pylab as plt
#get the filename
p=os.path.dirname(pySAXS.__file__)
dataFile="sample-lupolen-1800s.rgr"
completeDataFile=p+os.sep+"saxsdata"+os.sep+dataFile
#open data
completeData=numpy.loadtxt(completeDataFile)
data=completeData.transpose()

#----- plot data in matplotlib
datax=data[0]
datay=data[1]
plt.plot(datax,datay,linestyle='none',marker='.')
plt.show()

#----- Now we want to fit with pearsonVII
'''
par[0] : Amplitute of peak
par[1] : q at maximum of peak
par[2] : width of peak
par[3] : shape of peak
par[4] : background
'''
#best is to find some inital values
#1- background
background=datay.min()
#2- amplitude
amplitude=datay.max()-background
#3- q
qAtMax=0.03
width=0.03
#----- fit
from pySAXS.models import PearsonVII
d=PearsonVII() #declare model
d.q=datax       #q data to model
d.Arg=[amplitude,qAtMax,width,2.0,background] #initial parameters
print d.Arg
res=d.fit(datay) #FIT !!!
print "found : ",res
#----- plot result
d.Arg=res
i=d.getIntensity()
plt.plot(datax,datay,color='blue',linestyle='none',marker='o')
plt.plot(datax,i,color='red')
plt.show()

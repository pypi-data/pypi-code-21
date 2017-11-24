'''
example of use for open a data file (rgr) , plot, and fit
by a model
'''
import numpy
import pySAXS
import os
from guiqwt.pyplot import *
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
plot(datax,datay)#,linestyle='none',marker='o')
show()

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
plot(datax,datay)#,color='blue',linestyle='none',marker='o')
plot(datax,i)#,color='red')
show()

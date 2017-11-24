from pySAXS.mcsas import MCtools
from pySAXS.guisaxs.qt import QtMatplotlib
#from PyQt4 import QtGui, QtCore
import sys
#loading datas
from pySAXS.tools import filetools
import numpy
from time import sleep

datas="C:\winpython\python-2.7.9.amd64\Lib\site-packages\pySAXS\saxsdata\export-au.txt"
#datas="S:\\articles\momac\datas\ASCII_Gold_NP-MOMAC.txt"
q,I,E=filetools.openFile(datas)
'''app = QtGui.QApplication(sys.argv)
p=QtMatplotlib.QtMatplotlib()'''
#E=numpy.zeros(numpy.shape(q))
#p.show()
#p.addData(q, I, "experimental")
#p.replot()
from matplotlib.pyplot import bar
from matplotlib import pyplot as plt

#plot(q,I)
'''
A=MCtools.Analyze_1D(q,I,numpy.maximum(0.01*I,E),Nsph=200,Convcrit=1,\
                     Bounds=numpy.array([numpy.pi/numpy.max(q),numpy.pi/numpy.min(q)]),\
                     Rpfactor=1.5/3,Maxiter=1e5,Histscale='lin',drhosqr=1,Nreps=50)



#bar(A['Hx'][0:-1]*1e9,A['Hmean']/sum(A['Hmean']),width=A['Hwidth']*1e9,yerr=A['Hstd']/sum(A['Hmean']),color='orange',edgecolor='black',linewidth=1,zorder=2,ecolor='blue',capsize=5)

#p.addData(A['q'], A['Imean'], "fit")
#sys.exit(app.exec_())'''
print numpy.array(q)
'''
'c=MCtools.mcthread(q,I,numpy.maximum(0.01*I,E),Nsph=200,Convcrit=1,\
                     Bounds=numpy.array([numpy.pi/numpy.max(q),numpy.pi/numpy.min(q)]),\
                     Rpfactor=1.5/3,Maxiter=1e5,Histscale='lin',drhosqr=1,Nreps=2,Histbins=100)'''
c=MCtools.mcthread(q,I,numpy.maximum(0.01*I,E),Nsph=100,Convcrit=1,\
                     Bounds=numpy.array([00,500]),\
                     Rpfactor=1.5/3,Maxiter=1e5,Histscale='lin',drhosqr=1,Nreps=1,Histbins=200)
c.verbose=False
c.start()
while not c.stopped:
    sleep(1)
    print '---------',c.nr


A=c.A
#plt.bar(A['Hx'][0:-1],A['Hmean']/sum(A['Hmean']),width=A['Hwidth'],yerr=A['Hstd']/sum(A['Hmean']),color='orange',edgecolor='black',linewidth=1,zorder=2,ecolor='blue',capsize=5)
#plt.show()
s=A['Hx'][0:-1] #taille
V=A['Hmean']/sum(A['Hmean'])
r=(V*3/4.)**(1./3)    #radius from V

n=r/s  #number
#print n
print sum(n)

plt.figure(1)
plt.subplot(211)
plt.bar(A['Hx'][0:-1],A['Hmean']/sum(A['Hmean']),width=A['Hwidth'],yerr=A['Hstd']/sum(A['Hmean']),color='orange',edgecolor='black',linewidth=1,zorder=2,ecolor='blue',capsize=5)
plt.xlabel("size (nm)")
plt.ylabel('Volume-weighted particle size distribution values')
plt.subplot(212)
plt.bar(s,n,width=A['Hwidth'],yerr=A['Hstd']/sum(A['Hmean']),color='orange',edgecolor='black',linewidth=1,zorder=2,ecolor='blue',capsize=5)
plt.xlabel("size (nm)")
plt.ylabel('number')
plt.grid()
plt.show()
'''
# Two subplots, the axes array is 1-d
f, axarr = plt.subplots(2, sharex=True)

axarr[0].set_title('Sharing X axis')
axarr[0].
#plt.yscale('log', nonposy='clip')

'''
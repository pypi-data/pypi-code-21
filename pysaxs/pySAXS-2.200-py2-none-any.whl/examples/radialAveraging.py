'''
an example of radial averaging with pyFAI
'''

#from pyFAI import geometry
from pyFAI import azimuthalIntegrator
import fabio
import time
import os
import pySAXS
from numpy import *

from matplotlib import pylab

from pySAXS.tools import FAIsaxs
p=os.path.dirname(pySAXS.__file__)
imagefile=p+os.sep+"saxsdata"+os.sep+'OT-2012-10-12-tetradecanol-3600s.TIFF' #sample
maskfile=p+os.sep+"saxsdata"+os.sep+'mask.tif'#mask
xmlfile=p+os.sep+"saxsdata"+os.sep+'paramImageJ.xml' #parameters

imagefile='s://datas//test//OT-2013-02-20-tetradecanol-7200s.TIFF' #sample
maskfile='s://datas//test//mask2013.tif'#mask
xmlfile='s://datas//test//paramImageJfev2013.xml' #parameters
imagefile="X:/2017/2017-11-13-OT/2017-11-13-OT_0_09822.edf"
xmlfile="X:/2017/2017-11-13-OT/prefs_ld-x.xml"
#opening image
im=fabio.open(imagefile)
print imagefile ," opened"

# define fai
fai=azimuthalIntegrator.AzimuthalIntegrator()
'''
#------ first way 
# manually define the geomerty parameters
#g=geometry.Geometry()
print "set fit2d"
fai.setFit2D(730,centerX=2852,centerY=1625,tilt=7,pixelX=100,pixelY=100)
fai.set_wavelength(0.709*1e-9) #meters

# manually define mask
mask=fabio.open(maskfile)
maskdata=mask.data
maskdata=maskdata.astype(bool) #convert in bool
maskdata=invert(maskdata)
print "mask created"
#radial averaging
t0=time.time()
q,i=fai.integrate1d(im.data,1000,mask=maskdata,filename=imagefile+".rgr")
t1=time.time()
print "data averaged in ",t1-t0," s"
#radial averaging 2 with error
t0=time.time()
q,i,s=fai.integrate1d(im.data,1000,filename=imagefile+".rgr",error_model="poisson",mask=maskdata)
t1=time.time()
print "data averaged in ",t1-t0," s"
'''
#------ second way : import from ImageJ xml file 
fai=FAIsaxs.FAIsaxs()
fai.setGeometry(xmlfile)
maskdata=fai.getIJMask()
print fai.getMaskFilename()
#radial averaging 2 with error
t0=time.time()
q,i,s=fai.integrate1d(im.data,1000,mask=maskdata,filename=imagefile+".rgr",error_model="poisson")
t1=time.time()
print "data averaged in ",t1-t0," s"

#print r
pylab.plot(q,i)
pylab.show()

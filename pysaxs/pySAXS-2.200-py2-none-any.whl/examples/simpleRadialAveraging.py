'''
an example of simple radial averaging with pyFAI
'''
from pyFAI import azimuthalIntegrator
import fabio
import os
import pySAXS
#from numpy import *
from pySAXS.tools import FAIsaxs

p=os.path.dirname(pySAXS.__file__)
imagefile=p+os.sep+"saxsdata"+os.sep+'OT-2012-10-12-tetradecanol-3600s.TIFF' #sample
maskfile=p+os.sep+"saxsdata"+os.sep+'mask.tif'#mask
xmlfile=p+os.sep+"saxsdata"+os.sep+'paramImageJ.xml' #parameters

#opening image
im=fabio.open(imagefile)

# define fai
fai=FAIsaxs.FAIsaxs()
fai.setGeometry(xmlfile) #xml file 
maskdata=fai.getIJMask(maskfile)
q,i,s=fai.integrate1d(im.data,1000,mask=maskdata,filename=imagefile+".rgr",error_model="poisson")

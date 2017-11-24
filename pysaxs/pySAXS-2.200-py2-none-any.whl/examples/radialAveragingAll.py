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
import sys
from pySAXS.tools import filetools
from matplotlib import pylab

from pySAXS.tools import FAIsaxs
#p=os.path.dirname(pySAXS.__file__)
#imagefile=p+os.sep+"saxsdata"+os.sep+'OT-2012-10-12-tetradecanol-3600s.TIFF' #sample
#xmlfile='paramImageJ.xml' #set the parameter file


def process(xmlfile,files):
    paths=os.getcwd()
    l=filetools.listFiles(paths,files)
    # define fai
    fai=azimuthalIntegrator.AzimuthalIntegrator()
    fai=FAIsaxs.FAIsaxs()
    fai.setGeometry(xmlfile)
    maskdata=fai.getIJMask()
    print "Mask : ", fai.getMaskFilename()
    for imagefile in l:
        #opening image
        im=fabio.open(imagefile)
        print imagefile ," opened"
        #radial averaging with error
        t0=time.time()
        q,i,s=fai.integrate1d(im.data,1000,mask=maskdata,filename=imagefile+".rgr",error_model="poisson")
        t1=time.time()
        print "data averaged in ",t1-t0," s"
    

if __name__ == "__main__":
    arg=sys.argv
    print arg[1],arg[2]
    process(arg[1],arg[2])

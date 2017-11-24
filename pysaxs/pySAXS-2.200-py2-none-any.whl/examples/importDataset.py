'''
Example for importing and plotting data from a xml dataset
'''
import pySAXS
from pySAXS.guisaxs.dataset import *
import os
p=os.path.dirname(pySAXS.__file__)
dataFile="dataset_reglages.xml"
completeDataFile=p+os.sep+"saxsdata"+os.sep+dataFile
dt=getDataDictFromXMLFile(completeDataFile)
q=dt['OT-2012-06-07-tetra-3600s_TIFF.rgr'].q
i=dt['OT-2012-06-07-tetra-3600s_TIFF.rgr'].i

import matplotlib.pyplot as plt
plt.plot(q,i,color='red')
plt.show()


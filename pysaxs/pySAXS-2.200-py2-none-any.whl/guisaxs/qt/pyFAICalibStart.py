from guidata.dataset.dataitems import FileOpenItem, BoolItem, ButtonItem
from pyFAI.calibration import calib
import fabio
import guidata
import guidata.dataset.dataitems as di
import guidata.dataset.datatypes as dt
import os
import pyFAI, pyFAI.calibrant, pyFAI.detectors

_app = guidata.qapplication() 

class Processing(dt.DataSet):
    """Calib Start program"""
    
    """ list of calibrants """
    calibrants = pyFAI.calibrant.ALL_CALIBRANTS.keys()
    list_Calibrants = list(calibrants)
    list_Calibrants.sort()
    
    """ list of detectors """
    detectors = pyFAI.detectors.ALL_DETECTORS.keys()
    list_Detectors = list(detectors)
    list_Detectors.sort()
    
    waveLength = di.FloatItem("Wavelength (A) : ", "0.709")  # Default value 0.709
    detector = type = di.ChoiceItem("Detectors", (list_Detectors))
    calibrant = type = di.ChoiceItem("Calibrants", (list_Calibrants))
    fname = FileOpenItem("File :", ("tiff", "edf", "*"))
    polarization = di.StringItem("Polarization : ", default=None)
    distance = di.StringItem("Distance (mm) : ", default= None)
    fix_distance = BoolItem("fix distance")
    notilt = BoolItem("No Tilt")

param = Processing()
if param.edit():
    
    """
    Calib
    """
    cmd="pyFAI-calib.py "
    cmd+="-w "+str(param.waveLength)
    cmd+=" -D "+param.list_Detectors[param.detector]
    
    """
    Parameters 
    """
    if param.notilt:
        cmd+=" --no-tilt"
    
    if  param.polarization!='' :
        cmd+=" -P "+param.polarization
        
    if  param.distance!="" :
        cmd+=" -l "+param.distance
        
    if param.fix_distance:
        cmd+=" --fix-dist"
     
    
    cmd+=' "'+param.fname+'"'
    print cmd
    os.system(cmd)

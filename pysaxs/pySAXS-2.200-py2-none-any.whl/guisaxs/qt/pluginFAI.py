from pySAXS.guisaxs.qt import plugin
from pySAXS.guisaxs.qt import dlgQtFAI
from pySAXS.guisaxs.qt import dlgQtFAITest
from pySAXS.guisaxs.qt import dlgSurveyor
#from pySAXS.guisaxs.qt import startpyFAICalib

classlist=['pluginFAI','pluginTestFAI','pluginSurveyor']#,'pluginCalibStart',

class pluginFAI(plugin.pySAXSplugin):
    menu="Data Treatment"
    subMenu="Image"
    subMenuText="Fast Radial Averaging"
    icon="imshow.png"
    toolbar=True
    
    def execute(self):
        #get the preferences
        parameterfile=self.parent.pref.get("parameterfile",'pyFAI')
        ouputdir=self.parent.pref.get('outputdir','pyFAI')
        #display the FAI dialog box
        self.dlgFAI=dlgQtFAI.FAIDialog(self.parent,parameterfile,ouputdir)
        self.dlgFAI.show()


class pluginTestFAI(plugin.pySAXSplugin):
    menu="Data Treatment"
    subMenu="Image"
    subMenuText="Test Radial Averaging parameters"
    icon="image.png"
    
        
    def execute(self):
        parameterfile=self.parent.pref.get("parameterfile",'pyFAI')
        ouputdir=self.parent.pref.get('outputdir','pyFAI')
        #display the FAI dialog box
        self.dlgFAI=dlgQtFAITest.FAIDialogTest(self.parent,parameterfile,ouputdir)
        self.dlgFAI.show()
        
'''class pluginCalibStart(plugin.pySAXSplugin):
    menu="Data Treatment"
    subMenu="Image"
    subMenuText="Calibration tools"
    icon="magnifier.png"
    """Calib Start program"""
    detector = None
    calibrant = None
    def execute(self):
        self.calibStart = startpyFAICalib.CalibStart()
        self.calibStart.show()
        #self.calibStart.sleep(1) #I put this line because Calib close automatically when it is launched
'''
    
class pluginSurveyor(plugin.pySAXSplugin):
    menu="Data Treatment"
    subMenu="Image"
    subMenuText="Image Surveyor"
    icon="eye.png"
    toolbar=True
        
    def execute(self):
        #display the FAI dialog box
        parameterfile=self.parent.pref.get("parameterfile",'pyFAI')
        self.dlg=dlgSurveyor.SurveyorDialog(self.parent,parameterfile)
        self.dlg.show()
        
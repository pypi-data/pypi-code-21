class pySAXSplugin():
    
    menu="Plugins"
    subMenu="sub Plugins"
    subMenuText=""
    icon=None
    toolbar=False
    
    def __init__(self,parent,selectedData=None,noGUI=False):
        self.parent=parent #pySAXS GUI 
        self.data_dict=parent.data_dict
        self.selectedData=selectedData
        self.printTXT=parent.printTXT
        self.redrawTheList=parent.redrawTheList
        self.Replot=self.parent.Replot
        self.ListOfDatasChecked=parent.ListOfDatasChecked
        self.noGUI=noGUI
        self.workingdirectory=parent.workingdirectory
        self.referencedataSubtract=parent.referencedataSubtract
    
    def execute(self):
        '''
        execute
        '''
        #do nothing
        return
    
    def setParameters(self,parametersDict):
        '''
        want to execut with no gui,
        some parameters need to be transmitted
        parametersDict : dictionnary of parameters {'wavelength':1.542, ...}
        '''
        for key in parametersDict.keys():
            setattr(self,key,parametersDict[key])
        
    
    def setSelectedData(self,name):
        self.selectedData=name
    
    def setWorkingDirectory(self,filename):
        self.parent.setWorkingDirectory(filename)
    
    def getWorkingDirectory(self):
        return self.parent.workingdirectory
    
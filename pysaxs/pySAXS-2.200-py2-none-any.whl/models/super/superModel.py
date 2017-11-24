#import pySAXS.models as mdl

class superModel:
    Author="LIONS"  #name of Author
    name="supermodel" #name of super model
    modelList=[]
    q=None          #q range(x scale)
    #names=[]
    #arg=[]
    specific=False  #for specific model, set to true
    #print name
    formula=""
    variableDict={}#{'i0':'data1','i1':'data2',...}
    
    def __init__(self):
        #self.mylist=[]
        pass
    
    def appendModel(self,M,var=""):
        '''
        append a model on the list
        update the variableDict
        '''
        self.modelList.append(M)
        self.variableDict[var]=M.name
        
        
    def getModel(self,index):
        '''
        return a model instance from index
        '''
        if index<0 or index>=len(self.modelList):
            return None
        else:
            '''#try to get an instance of model
            element=self.modelList[index]
            modelname=element[0]
            #try:
            m=getattr(mdl,modelname)
            #if type(m)==type(mdl.Model):
            mi=m()
            if element[1]!=None:
                mi.Arg=element[1]
            return mi
            #except:
            return None'''
            return self.modelList[index]
            
    
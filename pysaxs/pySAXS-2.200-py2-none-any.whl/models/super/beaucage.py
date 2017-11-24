from pySAXS.models.super.superModel import superModel
from pySAXS.LS.LSsca import Qlogspace
from pySAXS.models import *

class Beaucage(superModel):
    '''
    by CG
    '''
    Author="CG"
    name="Beaucage" #name
    #print name
    q=Qlogspace(1e-4,0.15,500.)      #q range(x scale)
    modelList=[]
    formula="i1+i2+i3+i4"
    '''modelList.append(["GuinierModel",[135,130],"Guinier primary",q])
    modelList.append(["PorodPrim",[5.6249999999999995e-06,130],"Porod of primary",q])
    modelList.append(["GuinierModel",[15750.0,650.0],"Guinier of aggregate",q])
    modelList.append(["Fractal",[0.0045,650.0,2.45,130],"Fractal area",q])
    '''
    '''modelList.append(GuinierModel(q,[135,130],"Guinier primary"))
    modelList.append(PorodPrim(q,[5.6249999999999995e-06,130],"Porod of primary"))
    modelList.append(GuinierModel(q,[15750.0,650.0],"Guinier of aggregate"))
    modelList.append(Fractal(q,[0.0045,650.0,2.45,130],"Fractal area"))
    
    variableDict={'i0':'data1','i1':'data2'}'''
    def __init__(self):
        self.modelList=[]
        self.appendModel(GuinierModel(self.q,[135,130],name="Guinier primary"),'i1')
        self.appendModel(PorodPrim(self.q,[5.6249999999999995e-06,130],name="Porod of primary"),'i2')
        self.appendModel(GuinierModel(self.q,[15750.0,650.0],name="Guinier of aggregate"),'i3')
        self.appendModel(Fractal(self.q,[0.0045,650.0,2.45,130],name="Fractal area"),'i4')
        
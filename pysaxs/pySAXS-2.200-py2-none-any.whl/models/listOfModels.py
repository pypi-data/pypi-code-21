import pySAXS.models as mdl
import pySAXS.models.super as suprmdl

def listOfModels():
    l={}
    for modelname in dir(mdl):
        m=getattr(mdl,modelname)
        if type(m)==type(mdl.Model):
            try:
                mi=m()
            except:
                pass
            else:
                if isinstance(mi,mdl.Model) and modelname<>"Model" and not(mi.specific):
                    l[mi.name]=modelname
    return l

def listOfSuperModels():
    l={}
    for modelname in dir(suprmdl):
        m=getattr(suprmdl,modelname)
        if type(m)==type(suprmdl.superModel):
            try:
                mi=m()
            except:
                pass
            else:
                if isinstance(mi,suprmdl.superModel) and modelname<>"superModel" and not(mi.specific):
                    l[mi.name]=modelname
    return l

if __name__=='__main__':
    print listOfModels()

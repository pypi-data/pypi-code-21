from pySAXS.models.model import Model
import numpy

class PearsonVII(Model):
    '''
    PearsonVII model
    by OT : 5/7/2012
    '''
    
    def PearsonVIIFunction(self,q,par):
        """
        PearsonVII model 
        par[0] : Amplitute of peak
        par[1] : q at maximum of peak
        par[2] : width of peak
        par[3] : shape of peak
        par[4] : background
        """
        return par[0]/(1+((q-par[1])/par[2])**2)**par[3]+par[4]
    
    '''
    parameters definition
    '''
    def __init__(self):
        Model.__init__(self)
        self.IntensityFunc=self.PearsonVIIFunction #function
        self.name="PearsonVII"          #name of the model
        self.q=numpy.arange(0,1,0.01)      #q range(x scale)
        '''
        Arg=[100.,0.2,0.25,3,0]            #list of parameters
        Format=["%f","%f","%f","%f","%f"]      #list of c format
        istofit=[True,True,True,True,True]    #list of boolean for fitting
        
        Doc=["Amplitute of peak"\
                     ,"q at maximum of peak"\
                     ,"width of peak"\
                     ,"shape of peak"\
                     ,"background"] #list of description for parameters
        '''
        #a test for a more pythonic class system
        self.addParameter("Amplitute of peak",100.0)
        self.addParameter("q at maximum of peak",20.0)
        self.addParameter("width of peak",15)
        self.addParameter("shape of peak",3)
        self.addParameter("low level",0.0)
          
    
    Description="PearsonVII"  # description of model
    Author="Olivier Tache'"       #name of Author
    
    def prefit(self,Iexp):
        '''
        try to estimate some parameters from Iexp
        return a list of estimate parameters
        '''
        Iexp=numpy.array(Iexp)
        max=Iexp.max()
        min=Iexp.min()
        argmax=Iexp.argmax()
        qimax=self.q[argmax]
        qrange=self.q.max()-self.q.min()
        self.Arg=[max,qimax,qrange/20.0,2.0,min]
        return self.Arg
    
if __name__=="__main__":
    '''
    test code
    '''
    from matplotlib import pylab
    g=PearsonVII()
    x=g.q
    y=g.getIntensity()
    pylab.plot(x,y)
    pylab.show()
    
